#![recursion_limit = "256"]

/// The VAE is broken up into several parts
///
/// 1. an encoder
/// 2. the latent space, which is the bottleneck hidden layer
/// 3. a decoder
/// 4. A config for training hyperparams
/// 5. A training loop
///
/// Once we have a pre-trained VAE, we will use that as a prior for a GMM and
/// create a VaDE (Variational Autoencoder with a Gaussian Mixture Model). This
/// will allow us to cluster the latent space  
pub mod input_data;
