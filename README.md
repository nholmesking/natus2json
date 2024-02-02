Converts Natus files into JSON format.

All Python files are PEP-8 compliant.

Lines marked with "VERIFY" need to be verified to make sure they are compliant with the documentation.

Files:
- natus2json.py: converts Natus to JSON.
- json2edf.py: converts JSON (from natus2json.py) to EDF+. Currently non-functional.
- json2csv.py: converts JSON (from Natus ERD files) to CSV.
- edf_range.py: inputs an EDF and outputs a selected time range from the EDF.
- json2tkinter.py: inputs a JSON (from Natus ERD files) and generates an EEG visualization using Tkinter.
- json2dicom.py: inputs a JSON (from natus2json.py) and generates a DICOM file. Currently non-functional.
- json2dicom_altered.py: inputs a JSON (from Natus ERD files) and generates a nonstandard version of DICOM that uses less than half the amount of memory as the standard version.
- edf2dicom.py: inputs an EDF and converts it to standard DICOM. Assumes EDF+ from Natus ERD.
- dicom2edf.py: reverses edf2dicom.py.
- natus2men.py: converts Natus ERD into Memory-Efficient Natus (MEN) format. Currently only supports MEN-A.
- men2natus.py: reverses natus2men.py. Currently only supports MEN-A.
- supcp2tkinter.py: creates a Tkinter visualization from SupCP data.

See also:
- Document outlining results: https://docs.google.com/document/d/1vsgSZQMatsJYphpQt628trsgjX6-iKG2NcAN6Uziidk/edit?usp=sharing
- Document outlining proposal for new DICOM EEG standard: https://docs.google.com/document/d/1YgQ9ohIULXTKriNN6tGa4ld_DFnn-PmC7JIVVU7m1fg/edit?usp=sharing
- Documentation for MEN format: https://docs.google.com/document/d/1TXLMUNGjQWWs6DkvJWS4m2E8TF07oTX1L_vztQVU-4g/edit?usp=sharing
