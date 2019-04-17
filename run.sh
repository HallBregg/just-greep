#!/bin/bash

run_env="run_env/"
requirements_file="/conf/requirements_full.txt"

if [ -d "${run_env}" ]; then
  echo "Environment already exists. Activating ..."
  activate_env="source run_env/bin/activate"
  ${activate_env}
else
  echo "Run environment does not exist. Creating ..."
  create_env="virtualenv -p python3.7 run_env"
  ${create_env}

  if [ echo $? == 1 ]; then
    echo "Could not create virtual environment"
  fi
  activate_env="source run_env/bin/activate"
  ${activate_env}
  
  install_requirements="pip install -r ${requirements_file}"
  ${install_requirements}
fi
