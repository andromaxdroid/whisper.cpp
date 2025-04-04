.PHONY: build install clean

BUILD_DIR := $(HOME)/build
RUNTIME_OUTPUT_DIR := $(HOME)/build
LIB_OUTPUT_DIR := $(PREFIX)/lib/whisper


build:
	cmake -DWHISPER_BUILD_EXAMPLES=ON \
	      -DWHISPER_BUILD_TESTS=OFF \
	      -DCMAKE_BUILD_TYPE=Release \
	      -DCMAKE_RUNTIME_OUTPUT_DIRECTORY=$(RUNTIME_OUTPUT_DIR) \
	      -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=$(LIB_OUTPUT_DIR) \
	      -B $(BUILD_DIR)
	cmake --build $(BUILD_DIR) --target whisper-cli --config Release

	
		install -Dm755 $(BUILD_DIR)/bin/whisper-cli $(PREFIX)/bin/whisper; \
		install -Dm755 autofinal.py $(PREFIX)/bin/autotranscribe; \
	rm -rf $(BUILD_DIR)
	mkdir -p $(HOME)/.whisper/models
	cp -rf models/download-ggml-model.sh $(HOME)/.whisper/models/download-ggml-model.sh
	chmod +x $(HOME)/.whisper/models/download-ggml-model.sh
	

