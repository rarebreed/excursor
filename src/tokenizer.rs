/// crate for tokenizing text that will be used in the encoder of the VAE
use anyhow::Result;
use splintr::Tokenizer;
use splintr::pretrained::from_pretrained;

pub fn make_tokenizer(train_type: &str) -> Tokenizer {
    from_pretrained(train_type).unwrap()
}

/// A path to an S3 object including bucket and object key
///
/// Example: s3://bucket/key
pub struct S3Uri(String);

/// enum for data source
///
/// String: string containing the data that will be tokenized
/// File: file path to the data that will be tokenized
/// S3Uri: path to an S3 object including bucket and object key
///
pub enum DataSource {
    String(String),
    File(String),
    S3Uri(String),
}

/// struct for data loader
///
///
pub struct DataLoader {
    pub tokenizer: Tokenizer,
    pub data_source: DataSource,
}

/// Handles the process of loading data from a data source
pub trait DataSourceTrait {
    async fn load(&self) -> Result<Vec<u32>>;
}

/// Handles the process of normalizing text. For example, removing punctuation, converting to lowercase, or padding
pub trait Normalizer {
    fn normalize(&self, text: &str) -> Result<String>;
}

impl DataSourceTrait for DataLoader {
    async fn load(&self) -> Result<Vec<u32>> {
        match &self.data_source {
            DataSource::String(text) => Ok(self.tokenizer.encode(text)),
            DataSource::File(file_path) => {
                let text = std::fs::read_to_string(file_path)?;
                Ok(self.tokenizer.encode(&text))
            }
            DataSource::S3Uri(s3_uri) => {
                let config = aws_config::load_from_env().await;
                let client = Client::new(&config);
                let Some((bucket, prefix)) = s3_uri.split_once("/") else {
                    return Err(anyhow::anyhow!("Invalid S3 URI"));
                };
                let text = client
                    .get_object()
                    .bucket(bucket)
                    .key(prefix)
                    .send()
                    .await?
                    .body
                    .collect()
                    .await?;
                Ok(self.tokenizer.encode(&text))
            }
        }
    }
}
