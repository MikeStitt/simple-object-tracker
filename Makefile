all : 
	protoc --python_out=./ test.proto
	pyuic4 -x test.ui  -o test_ui.py