Docker Configuration for Flight Data Analyzer
=============================================

This dockerfile requires an additional file to build.  This file is 
`gdfuse_config.zip` and contains the configuration for the googledrive-ocamlfuse
network mount.  This file is NOT provided on this github for security purposes,
as the mounted dataset may contain sensitive personally identifiable 
information.  For access to this file, please contact Nathan Hui at 
nthui@eng.ucsd.edu or Engineers for Exploration.

To use this dockerfile:

1.	`cd $(FLIGHT_DATA_ANALYZER)/docker/`
2.	`docker build -t ece143 .`
3.	`./run $(CODE_ROOT)` where `$(CODE_ROOT)` is the root directory of the
	relevant codebase to run.

	