# Simple Real-Time Telemetry Dashboard for F1 2021
This project shows an example of how to use the UDP data stream from [F1 2023][1] video game to visualize real-time data by ingesting the data into MongoDB. Additionally, this data can be used for post race performance analysis.

Thanks to Codemasters for providing this awesome feature. You can check the forum to see all data that is available from their [F1 2023 UDP Specification][2].

[1]: https://www.ea.com/de-de/games/f1/f1-23
[2]: https://answers.ea.com/t5/General-Discussion/F1-23-UDP-Specification/m-p/12633159

## How to run
Create a .env file inside the project folder and include the necessary env vars.

    ## Defaults from F1 UDP Telemetry
    F1_UDP_SERVER_ADDRESS=127.0.0.1
    F1_UDP_SERVER_PORT=20777

    ## Connection string including credentials for your MongoDB
    MONGODB_CONNECTION_STRING=mongodb://username:password@127.0.0.1:27017/

Once you have installed the requirements from `requirements.txt` run main.py inside the f1_telemetry folder.

    python -m f1_telemetry.main