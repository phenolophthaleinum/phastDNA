#
# Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

CXX = c++
CXXFLAGS = -pthread -std=c++17 -march=native
OBJS = args.o dictionary.o productquantizer.o matrix.o qmatrix.o vector.o model.o utils.o fasttext.o
INCLUDES = -I.

opt: CXXFLAGS += -O3 -funroll-loops -DNDEBUG
opt: fastdna

debug: CXXFLAGS += -g -O0 -fno-inline
debug: fastdna

args.o: src/args.cc src/args.h
	$(CXX) $(CXXFLAGS) -c src/args.cc

dictionary.o: src/dictionary.cc src/dictionary.h src/args.h
	$(CXX) $(CXXFLAGS) -c src/dictionary.cc

productquantizer.o: src/productquantizer.cc src/productquantizer.h src/utils.h
	$(CXX) $(CXXFLAGS) -c src/productquantizer.cc

matrix.o: src/matrix.cc src/matrix.h src/utils.h
	$(CXX) $(CXXFLAGS) -c src/matrix.cc

qmatrix.o: src/qmatrix.cc src/qmatrix.h src/utils.h
	$(CXX) $(CXXFLAGS) -c src/qmatrix.cc

vector.o: src/vector.cc src/vector.h src/utils.h
	$(CXX) $(CXXFLAGS) -c src/vector.cc

model.o: src/model.cc src/model.h src/args.h
	$(CXX) $(CXXFLAGS) -c src/model.cc

utils.o: src/utils.cc src/utils.h
	$(CXX) $(CXXFLAGS) -c src/utils.cc

fasttext.o: src/fasttext.cc src/*.h
	$(CXX) $(CXXFLAGS) -c src/fasttext.cc

fastdna: $(OBJS) src/fasttext.cc
	$(CXX) $(CXXFLAGS) $(OBJS) src/main.cc -o fastdna -lstdc++fs

clean:
	rm -rf *.o fasttext
