#![recursion_limit = "256"]

/// The VAE is broken up into several parts
/// 1. an encoder
/// 2. the latent space, which is the bottleneck hidden layer
/// 3. a decoder
/// 4. A config for training hyperparams
/// 5.
pub mod tokenizer;
