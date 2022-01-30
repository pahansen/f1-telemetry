# Simple Telemetry Dashboard for F1 2021
This project shows an example of how to use the UDP data stream from [F1 2021][1] video game. It includes parsing data from binary format into Python classes, working with the data in a pandas data frame and finally visualizing this data in Plotly / Dash. Only a subset of the available data (PacketCarTelemetry) was used to produce a minimalistic dashboard:

![F1 2021 Dashboard Example](https://github.com/pahansen/f1-2021-telemetry-dashboard/blob/main/DashF1.jpg?raw=true)

Within the dash app, the "Interval" component was used to refresh data every second based on data that was buffered from the UDP stream. The example shows data, that was streamed to the dashboard during a drive on the Bahrain race circuit.

Thanks to Codemasters for providing this awesome feature. You can check the forum to see all data that is available from their [F1 2021 UDP Specification][2].


[1]: https://www.ea.com/de-de/games/f1/f1-2021
[2]: https://forums.codemasters.com/topic/80231-f1-2021-udp-specification/

## Remarks
The code shown in this project should only serve as a little playground for getting your hands on F1 2021 data in an easy way without too many dependencies on technologies for streaming data properly :-).

