Converts Natus files into JSON format.

All Python files are PEP-8 compliant.

Lines marked with "VERIFY" need to be verified to make sure they are compliant with the documentation.

Files:
- natus2json.py: converts Natus to JSON.
- json2edf.py: converts JSON (from natus2json.py) to EDF+. Currently non-functional.
- json2csv.py: converts JSON (from Natus ERD files) to CSV.
- edf_range.py: inputs an EDF and outputs a selected time range from the EDF.
- json2tkinter.py: inputs a JSON (from Natus ERD files) and generates an EEG visualization using Tkinter.
- json2dicom.py: inputs a JSON (from natus2json.py) and generates a DICOM files. Currently non-functional.
