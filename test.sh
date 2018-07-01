#!/bin/bash
FILES=(
  "src/kobuki/kobuki_node/src/nodelet/kobuki_nodelet.cpp"
  "src/urdf/urdf/src/model.cpp"
  "src/urdf/urdf/src/rosconsole_bridge.cpp"
)
/opt/bond/bond ${FILES[@]}
