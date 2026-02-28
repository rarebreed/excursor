# Road map

High level view of things to work on in the project.

1. Create a small game database service that will create test logs
    - It will have two tables: one for player data and one for logs
    - It will have several internal components which can be specified to fail
    - It will have mocked out external components which can be specified to fail
    - It will have an interface to control the service and any errors it generates
    - It will be written in python and use fastapi
    - It will use loguru for logging
    - It will use daft for data processing
    - It will use lancedb for storage
1. Create a runner for the game database service
    - It will generate fake player data
    - It will have configurations for different types of errors to inject
    - It will have configurations for different types of external component failures to inject
    - The generated logs will be sent to the game database service
    - It will be written in python and use fastapi
1. Collect the logs from the game database service
    - It will collect the logs from the game database service
    - It will batch the logs and create embeddings
    - It will store the embeddings in lancedb
1. Run the embedder on the logs
    - It will create embeddings for the logs
    - It will store the embeddings in game database service
1. Write the initial VAE model
    - Input layer takes the embeddings as a Batch in burn
    - First hidden layer will reduce dimensionality
        - What kind of regularization and what kind of activation function?
    - Second hidden layer as above, but reduce dimensionality