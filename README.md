# Simple Telemetry Dashboard for F1 2021
This project shows an example of how to use the UDP data stream from [F1 2021][1] video game to visualize real-time data. It includes parsing data from binary format into Python classes, working with the data in a pandas data frame and finally visualizing this data in Plotly / Dash. Only a subset of the available data (PacketCarTelemetry) was used to produce a minimalistic dashboard:

![F1 2021 Dashboard Example](https://github.com/pahansen/f1-2021-telemetry-dashboard/blob/main/DashF1.JPG)

Within the dash app, the "Interval" component was used to refresh data every 500ms based on data that was written to InfluxDB from the UDP stream. The example shows data, that was streamed to the dashboard during a drive on the Mexican race circuit.

Thanks to Codemasters for providing this awesome feature. You can check the forum to see all data that is available from their [F1 2021 UDP Specification][2].


[1]: https://www.ea.com/de-de/games/f1/f1-2021
[2]: https://forums.codemasters.com/topic/80231-f1-2021-udp-specification/

## Remarks
At the moment, this project only shows a basic set of visualizations. Mainly, should give an idea on how it is possible to work with real-time telemetry data in Plotly - Dash. However, whenever there is time I will include more visualizations and also integrate the dash app into docker compose.