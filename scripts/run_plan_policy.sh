#!/bin/bash

model_dir=/home/mbhenaff/projects/pytorch-Traffic-Simulator/scratch/models_v9/

method=policy-svg

for policy_model in ${model_dir}/policy_networks/svg*npred=40*ureg=0.01*.model; do 
    echo $(basename $policy_model)
    sbatch submit_plan_policy.slurm $method $model_dir $(basename $policy_model)
done
