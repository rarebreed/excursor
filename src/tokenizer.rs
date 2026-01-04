/// crate for tokenizing text that will be used in the encoder of the VAE

use splintr::Tokenizer;
use splintr::pretrained::from_pretrained;

pub fn encode(
    text: &str,
    tokenizer: Option<Tokenizer>,
) -> Result<(Tokenizer, Vec<u32>), Box<dyn std::error::Error>> {
    let tokenizer = match tokenizer {
        Some(tokenizer) => tokenizer,
        None => from_pretrained("llama3")?,
    };

    let tokens = tokenizer.encode(text);

    Ok((tokenizer, tokens))
}