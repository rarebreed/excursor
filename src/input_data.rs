//! crate for loading data that will be used in the encoder of the VAE
//!
//! It includes a tokenizer, a data source, and a normalizer

use anyhow::Result;
use aws_config::BehaviorVersion;
use aws_sdk_s3::Client;
use aws_sdk_s3::operation::get_object::GetObjectOutput;
use aws_sdk_s3::primitives::AggregatedBytes;
use splintr::Tokenizer;
use splintr::pretrained::from_pretrained;

pub fn make_tokenizer(train_type: &str) -> Tokenizer {
    from_pretrained(train_type).unwrap()
}

/// A path to an S3 object including bucket and object key
///
/// Example: s3://bucket/key
// pub struct S3Uri(String);

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

/// struct for log data
///
/// Represents large text files such as logs or books
pub struct LogDataLoader {
    /// The tokenizer to use for tokenizing the data
    pub tokenizer: Tokenizer,
    /// The data source to use for loading the data
    pub data_source: DataSource,
    /// The maximum length of a line to use for tokenizing the data
    pub max_line_length: usize,
}

/// Handles the process of loading data from a data source
pub trait DataLoader {
    fn load(&self) -> Result<Vec<u32>>;
}

/// Handles the process of normalizing text. For example, removing punctuation, converting to lowercase, or padding
pub trait Normalizer {
    fn normalize(&self, text: &str) -> Result<String>;
}

impl DataLoader for LogDataLoader {
    fn load(&self) -> Result<Vec<u32>> {
        match &self.data_source {
            DataSource::String(text) => {
                let normalized_text = self.normalize(text)?;
                Ok(self.tokenizer.encode(&normalized_text))
            }
            DataSource::File(file_path) => {
                let text = std::fs::read_to_string(file_path)?;
                let normalized_text = self.normalize(&text)?;
                Ok(self.tokenizer.encode(&normalized_text))
            }
            DataSource::S3Uri(s3_uri) => {
                let rt = tokio::runtime::Runtime::new().expect("Failed to create Tokio runtime");
                let config = rt.block_on(aws_config::load_defaults(BehaviorVersion::latest()));
                let client = Client::new(&config);
                let Some((bucket, prefix)) = s3_uri.split_once("/") else {
                    return Err(anyhow::anyhow!("Invalid S3 URI"));
                };

                // Download the file from S3
                let text: AggregatedBytes = rt.block_on(async move {
                    let response: GetObjectOutput = client
                        .get_object()
                        .bucket(bucket)
                        .key(prefix)
                        .send()
                        .await?;
                    let body: AggregatedBytes = response.body.collect().await?;
                    Ok::<_, anyhow::Error>(body)
                })?;
                let vec_text = text.to_vec();
                let str_text = std::str::from_utf8(&vec_text)?;
                let normalized_text = self.normalize(str_text)?;
                Ok(self.tokenizer.encode(&normalized_text))
            }
        }
    }
}

impl Normalizer for LogDataLoader {
    /// For our use case, which is loading text files, we need to check for a few things:
    /// 1. get the largest text line
    /// 2. if the largest text line is longer than max_line_length, split it into multiple lines
    fn normalize(&self, text: &str) -> Result<String> {
        // TODO: parallelize this
        let lines = text.split('\n').map(|line| {
            if line.len() > self.max_line_length {
                line.chars().take(self.max_line_length).collect::<String>()
            } else {
                line.to_string()
            }
        });
        Ok(lines.collect::<Vec<String>>().join("\n"))
    }
}

pub struct TextDataLoaderBuilder {
    tokenizer: Option<Tokenizer>,
    data_source: Option<DataSource>,
    max_line_length: Option<usize>,
}

impl TextDataLoaderBuilder {
    pub fn new() -> Self {
        Self {
            tokenizer: None,
            data_source: None,
            max_line_length: None,
        }
    }

    pub fn tokenizer(mut self, tokenizer: Tokenizer) -> Self {
        self.tokenizer = Some(tokenizer);
        self
    }

    pub fn train_type(mut self, train_type: &str) -> Self {
        self.tokenizer = Some(make_tokenizer(train_type));
        self
    }

    pub fn data_source(mut self, data_source: DataSource) -> Self {
        self.data_source = Some(data_source);
        self
    }

    pub fn max_line_length(mut self, max_line_length: usize) -> Self {
        self.max_line_length = Some(max_line_length);
        self
    }

    pub fn build(self) -> Result<LogDataLoader> {
        let tokenizer = self
            .tokenizer
            .ok_or_else(|| anyhow::anyhow!("Tokenizer must be set"))?;
        let data_source = self
            .data_source
            .ok_or_else(|| anyhow::anyhow!("Data source must be set"))?;
        let max_line_length = self
            .max_line_length
            .ok_or_else(|| anyhow::anyhow!("Max line length must be set"))?;

        Ok(LogDataLoader {
            tokenizer,
            data_source,
            max_line_length,
        })
    }
}

impl LogDataLoader {
    pub fn builder() -> TextDataLoaderBuilder {
        TextDataLoaderBuilder::new()
    }

    pub fn new(train_type: &str, data_source: DataSource, max_line_length: usize) -> Self {
        Self::builder()
            .train_type(train_type)
            .data_source(data_source)
            .max_line_length(max_line_length)
            .build()
            .unwrap()
    }
}

pub fn create_embeddings(data: DataSource) -> Result<Vec<u32>, Box<dyn std::error::Error>> {
    let log_data_loader = LogDataLoader::builder()
        .train_type("deepseek_v3")
        .data_source(data)
        .max_line_length(40)
        .build()?;
    let tokens = log_data_loader.load()?;
    println!("Tokens: {:?}", tokens);
    Ok(tokens)
}
