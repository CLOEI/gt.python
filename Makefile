CXX = clang++

all: enet/enet.dll requirements

requirements:
	@echo "Installing Python requirements..."
	pip install -r requirements.txt
	
enet/enet.dll: enet/enet.cpp
	@echo "Compiling enet..."
	$(CXX) enet/enet.cpp -shared -DENET_DLL -DENET_IMPLEMENTATION -o $@
