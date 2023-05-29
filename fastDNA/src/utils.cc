/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#include "utils.h"

#include <ios>
// #include <sstream>
// #include <vector>
// #include <algorithm>

namespace fasttext {

namespace utils {

  int64_t size(std::ifstream& ifs) {
    ifs.seekg(std::streamoff(0), std::ios::end);
    return ifs.tellg();
  }

  void seek(std::ifstream& ifs, int64_t pos) {
    ifs.clear();
    ifs.seekg(std::streampos(pos));
  }

  // std::vector<std::string> splitString(const std::string& input, char delimiter) {
  //   std::replace(input.begin(), input.end(), delimiter, ' ');
  //   std::vector<std::string> splitted;
  //   std::stringstream ss(input);
  //   std::string temp;
  //   while (ss >> temp)
  //     splitted.push_back(temp);
  // }
}

}
