mod input_data;

use input_data::DataSourceTrait;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let log_data_loader = input_data::LogDataLoader::builder()
        .train_type("deepseek_v3")
        .data_source(input_data::DataSource::String(r"12:34:56 INFO Hello, world!
        12:34:57 INFO here's another line
        12:34:58 INFO and another
        12:34:59 INFO and one that is really long to test the max line length functionality of the log data loader. so we can see if it splits the line correctly.
        ".to_string()))
        .max_line_length(40)
        .build()?;
    let tokens = log_data_loader.load()?;
    println!("Tokens: {:?}", tokens);
    Ok(())
}
