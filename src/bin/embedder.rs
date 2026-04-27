use std::path::PathBuf;

use clap::Parser;
use excursor::input_data::{DataSource, create_embeddings};

/// Simple program to greet a person
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Max length for each line
    #[arg(short, long, default_value_t = 120)]
    max_len: usize,

    /// Optional path to file
    #[arg(short, long)]
    path: Option<PathBuf>,
}

fn main() {
    let args = Args::parse();

    // let data = DataSource::String("Hello, World!".to_string());
    // TODO: add a new arg so we can pattern match on which DataSource to use
    if let Some(path) = args.path {
        let s: &str = path.to_str().expect("Unable to get path string");
        let data = DataSource::File(s.to_owned());

        match create_embeddings(data, args.max_len) {
            Ok(tokens) => println!("Success: {:?}", tokens),
            Err(e) => eprintln!("Error {}", e),
        }
    } else {
        println!("")
    }
}
