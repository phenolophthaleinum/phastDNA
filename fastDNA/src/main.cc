/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#include <iostream>
#include <sstream>
#include <queue>
#include <iomanip>
#include "fasttext.h"
#include "args.h"

using namespace fasttext;

void printUsage() {
  std::cerr
    << "usage: fastdna <command> <args>\n\n"
    << "The commands supported by fastdna are:\n\n"
    << "  supervised              train a supervised classifier\n"
    << "  quantize                quantize a model to reduce the memory usage\n"
    << "  test                    evaluate a supervised classifier\n"
    << "  predict                 predict most likely labels\n"
    << "  predict-prob            predict most likely labels with probabilities\n"
    // << "  skipgram                train a skipgram model\n"
    // << "  cbow                    train a cbow model\n"
    << "  print-word-vectors      print word vectors given a trained model\n"
    // << "  print-ngrams            print ngrams given a trained model and word\n"
    // << "  nn                      query for nearest neighbors\n"
    // << "  analogies               query for analogies\n"
    // << "  dump                    dump arguments,dictionary,input/output vectors\n"
    << std::endl;
}

void printQuantizeUsage() {
  std::cerr
    << "usage: fastdna quantize <args>"
    << std::endl;
}

void printTestUsage() {
  std::cerr
    << "usage: fastdna test <model> <test-data> [<k>] [<th>]\n\n"
    << "  <model>      model filename\n"
    << "  <test-data>  test data filename (if -, read from stdin)\n"
    << "  <model>      test labels filename\n"
    << "  <k>          (optional; 1 by default) predict top k labels\n"
    << "  <th>         (optional; 0.0 by default) probability threshold\n"
    << std::endl;
}

void printPredictUsage() {
  std::cerr
    << "usage: fastdna predict[-prob] <model> <test-data> [<k>] [<th>]\n\n"
    << "  <model>      model filename\n"
    << "  <test-data>  test data filename (if -, read from stdin)\n"
    << "  <k>          (optional; 1 by default) predict top k labels\n"
    << "  <th>         (optional; 0.0 by default) probability threshold\n"
    << std::endl;
}

void printPrintWordVectorsUsage() {
  std::cerr
    << "usage: fastdna print-word-vectors <model>\n\n"
    << "  <model>      model filename\n"
    << std::endl;
}

void printPrintNgramsUsage() {
  std::cerr
    << "usage: fastdna print-ngrams <model> <word>\n\n"
    << "  <model>      model filename\n"
    << "  <word>       word to print\n"
    << std::endl;
}

void quantize(const std::vector<std::string>& args) {
  Args a = Args();
  if (args.size() < 3) {
    printQuantizeUsage();
    a.printHelp();
    exit(EXIT_FAILURE);
  }
  a.parseArgs(args);
  FastText fasttext;
  // parseArgs checks if a->output is given.
  fasttext.loadModel(a.output + ".bin");
  fasttext.quantize(a);
  fasttext.saveModel();
  exit(0);
}

void printNNUsage() {
  std::cout
    << "usage: fastdna nn <model> <k>\n\n"
    << "  <model>      model filename\n"
    << "  <k>          (optional; 10 by default) predict top k labels\n"
    << std::endl;
}

void printAnalogiesUsage() {
  std::cout
    << "usage: fastdna analogies <model> <k>\n\n"
    << "  <model>      model filename\n"
    << "  <k>          (optional; 10 by default) predict top k labels\n"
    << std::endl;
}

void printDumpUsage() {
  std::cout
    << "usage: fastdna dump <model> <option>\n\n"
    << "  <model>      model filename\n"
    << "  <option>     option from args,dict,input,output"
    << std::endl;
}

void test(const std::vector<std::string>& args) {
  if (args.size() < 5 || args.size() > 7) {
    printTestUsage();
    exit(EXIT_FAILURE);
  }
  int32_t k = 1;
  real threshold = 0.0;
  if (args.size() > 5) {
    k = std::stoi(args[5]);
    if (args.size() == 7) {
      threshold = std::stof(args[6]);
    }
  }
  bool paired_end = args[1] == "test-paired";
  FastText fasttext;
  // std::cerr << "Loading Model" << std::endl;
  fasttext.loadModel(args[2]);
  // std::cerr << "Model Loaded" << std::endl;

  std::tuple<int64_t, double, double> result;
  std::string infile = args[3];
  std::string labelfile = args[4];
  if (infile == "-") {
    // result = fasttext.test(std::cin, k, threshold);
  } else {
    std::ifstream ifs(infile);
    if (!ifs.is_open()) {
      std::cerr << "Test file cannot be opened!" << std::endl;
      exit(EXIT_FAILURE);
    }
    std::ifstream labels(labelfile);
    if (!ifs.is_open()) {
      std::cerr << "Label file cannot be opened!" << std::endl;
      exit(EXIT_FAILURE);
    }
    if (paired_end) {
      result = fasttext.test_paired(ifs, labels, k, threshold);
    } else {
      result = fasttext.test(ifs, labels, k, threshold);
    }
    ifs.close();
  }
  std::cout << "N" << "\t" << std::get<0>(result) << std::endl;
  std::cout << std::setprecision(3);
  std::cout << "P@" << k << "\t" << std::get<1>(result) << std::endl;
  std::cout << "R@" << k << "\t" << std::get<2>(result) << std::endl;
  std::cerr << "Number of examples: " << std::get<0>(result) << std::endl;
}

void predict(const std::vector<std::string>& args) {
  if (args.size() < 4 || args.size() > 6) {
    printPredictUsage();
    exit(EXIT_FAILURE);
  }
  int32_t k = 1;
  real threshold = 0.0;
  bool paired_end = (args[1] == "predict-paired" || args[1] == "predict-paired-prob");

  if (args.size() > 4) {
    k = std::stoi(args[4]);
    if (args.size() == 6) {
      threshold = std::stof(args[5]);
    }
  }

  bool print_prob = (args[1] == "predict-prob" || args[1] == "predict-paired-prob");
  FastText fasttext;
  fasttext.loadModel(std::string(args[2]));

  std::string infile(args[3]);
  if (infile == "-") {
    fasttext.predict(std::cin, k, paired_end, print_prob, threshold);
  } else {
    std::ifstream ifs(infile);
    if (!ifs.is_open()) {
      std::cerr << "Input file cannot be opened!" << std::endl;
      exit(EXIT_FAILURE);
    }
    fasttext.predict(ifs, k, paired_end, print_prob, threshold);
    ifs.close();
  }

  exit(0);
}

void printWordVectors(const std::vector<std::string> args) {
    //!=3 if text !=4 for binary
  if (args.size() != 4) {
    printPrintWordVectorsUsage();
    exit(EXIT_FAILURE);
  }
  FastText fasttext;
  fasttext.loadModel(std::string(args[2]));
  std::string word;
  Vector vec(fasttext.getDimension());
  //uncomment for binary
  std::ofstream file;
  file.open((args[3] + ".vec").c_str(), std::ios_base::binary | std::ios_base::out);
  //uncomment to show computed filenames
  //std::cout << (args[3] + ".vec").c_str() << std::endl;
  while (1) {
    fasttext.getWordVector(vec, std::cin);
    if (std::cin.eof()) { break; }
    //txt
    //std::cout << vec << std::endl;
    
    // MM edit
    //file.write((char*)(&vec[0]), vec.size() * sizeof(vec[0]));
    // 
    // 
    //uncomment for binary
    file.write((char*)vec.data(), vec.size() * sizeof(real));
    
    //file.put('\n');
    //std::string vec_str = vec.c_str();
    // doesnt work:
    //std::string vec_str{ std::begin(vec), std::end(vec) };
    //std::cout << vec.data() << std::endl;
    //std::cout << vec.data().c_str() << std::endl;

    //std::string vec_str;
    //std::stringstream ss;
    //ss << vec;
    //vec_str = ss.str();
    ////std::cout << vec_str << std::endl;
    //file.write(vec_str.c_str(), vec_str.size());
    //file.put('\n');
    //file.write((char*)(&vec_str), vec_str.size() * sizeof(std::string));
    //file << vec << "\n";
  }
  //binary
  file.close();
  exit(0);
}

void printNgrams(const std::vector<std::string> args) {
  if (args.size() != 4) {
    printPrintNgramsUsage();
    exit(EXIT_FAILURE);
  }
  FastText fasttext;
  fasttext.loadModel(std::string(args[2]));
  fasttext.ngramVectors(std::string(args[3]));
  exit(0);
}

void nn(const std::vector<std::string> args) {
  int32_t k;
  if (args.size() == 3) {
    k = 10;
  } else if (args.size() == 4) {
    k = std::stoi(args[3]);
  } else {
    printNNUsage();
    exit(EXIT_FAILURE);
  }
  FastText fasttext;
  fasttext.loadModel(std::string(args[2]));
  std::string queryWord;
  std::shared_ptr<const Dictionary> dict = fasttext.getDictionary();
  Vector queryVec(fasttext.getDimension());
  Matrix wordVectors(dict->nwords(), fasttext.getDimension());
  std::cerr << "Pre-computing word vectors...";
  fasttext.precomputeWordVectors(wordVectors);
  std::cerr << " done." << std::endl;
  std::set<std::string> banSet;
  std::cout << "Query word? ";
  std::vector<std::pair<real, std::string>> results;
  while (std::cin >> queryWord) {
    banSet.clear();
    banSet.insert(queryWord);
    fasttext.getWordVector(queryVec, queryWord);
    fasttext.findNN(wordVectors, queryVec, k, banSet, results);
    for (auto& pair : results) {
      std::cout << pair.second << " " << pair.first << std::endl;
    }
    std::cout << "Query word? ";
  }
  exit(0);
}

void analogies(const std::vector<std::string> args) {
  int32_t k;
  if (args.size() == 3) {
    k = 10;
  } else if (args.size() == 4) {
    k = std::stoi(args[3]);
  } else {
    printAnalogiesUsage();
    exit(EXIT_FAILURE);
  }
  FastText fasttext;
  fasttext.loadModel(std::string(args[2]));
  fasttext.analogies(k);
  exit(0);
}

void train(const std::vector<std::string> args) {
  Args a = Args();
  a.parseArgs(args);
  FastText fasttext;
  std::ofstream ofs(a.output+".bin");
  if (!ofs.is_open()) {
    throw std::invalid_argument(a.output + ".bin cannot be opened for saving.");
  }
  ofs.close();
  fasttext.train(a);
  fasttext.saveModel();
  // mm change
  if (a.saveVec)
  {
	fasttext.saveVectors();  
  }
  //
  if (a.saveOutput) {
    fasttext.saveOutput();
  }
}

void dump(const std::vector<std::string>& args) {
  if (args.size() < 4) {
    printDumpUsage();
    exit(EXIT_FAILURE);
  }

  std::string modelPath = args[2];
  std::string option = args[3];

  FastText fasttext;
  fasttext.loadModel(modelPath);
  if (option == "args") {
    fasttext.getArgs().dump(std::cout);
  } else if (option == "dict") {
    fasttext.getDictionary()->dump(std::cout);
  } else if (option == "input") {
    if (fasttext.isQuant()) {
      std::cerr << "Not supported for quantized models." << std::endl;
    } else {
      fasttext.getInputMatrix()->dump(std::cout);
    }
  } else if (option == "output") {
    if (fasttext.isQuant()) {
      std::cerr << "Not supported for quantized models." << std::endl;
    } else {
      fasttext.getOutputMatrix()->dump(std::cout);
    }
  } else {
    printDumpUsage();
    exit(EXIT_FAILURE);
  }
}

int main(int argc, char** argv) {
  std::vector<std::string> args(argv, argv + argc);
  if (args.size() < 2) {
    printUsage();
    exit(EXIT_FAILURE);
  }
  std::string command(args[1]);
  if (command == "skipgram" || command == "cbow" || command == "supervised") {
    train(args);
  } else if (command == "test" || command == "test-paired") {
    test(args);
  } else if (command == "quantize") {
    quantize(args);
  } else if (command == "print-word-vectors") {
    printWordVectors(args);
  } else if (command == "print-ngrams") {
    printNgrams(args);
  } else if (command == "nn") {
    nn(args);
  } else if (command == "analogies") {
    analogies(args);
  } else if (command == "predict" || command == "predict-prob" ||
             command == "predict-paired" || command == "predict-paired-prob") {
    predict(args);
  } else if (command == "dump") {
    dump(args);
  } else {
    printUsage();
    exit(EXIT_FAILURE);
  }
  return 0;
}
