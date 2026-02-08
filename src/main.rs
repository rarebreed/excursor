mod tokenizer;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (_, tokens) = tokenizer::encode("Hello, world!", None)?;
    println!("Tokens: {:?}", tokens);
    Ok(())
}
