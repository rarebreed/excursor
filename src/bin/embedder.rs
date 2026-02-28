use excursor::input_data::{DataSource, create_embeddings};

fn main() {
    let data = DataSource::String("Hello, World!".to_string());
    match create_embeddings(data) {
        Ok(tokens) => println!("Success: {:?}", tokens),
        Err(e) => eprintln!("Error {}", e),
    }
}
