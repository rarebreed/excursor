//! crate for configuration of the VAE  
//! 
//! Uses a burn config struct to store the configuration of the VAE
//! 
//! 

use burn::config::Config;

#[derive(Config)]
pub struct VAEConfig {
    /// The size of the vocabulary
    pub vocab_size: usize,
    /// The maximum length of a sequence
    pub max_seq_len: usize,
    /// The dimension of the embedding (inpput size of the VAE)
    pub embedding_dim: usize,
    /// The dimension of the hidden layer (size of the encoder and decoder)
    pub hidden_dim: usize,
    /// The dimension of the latent space
    pub latent_dim: usize,
    /// The dropout rate
    pub dropout: f32,
    /// The learning rate
    pub learning_rate: f32,
    /// The batch size
    pub batch_size: usize,
    /// The number of epochs
    pub num_epochs: usize,
}