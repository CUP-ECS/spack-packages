## About:
CUP-ECS internal spack package respository

## Setup:

#### To register this repository, add the following lines to your ~/.spack/repos.yaml file:
```
repos:
  cupecs:
    git: git@github.com:CUP-ECS/spack-packages.git
    destination: ~/cupecs # Modify to where you want this repository cloned
```

#### For packages that include `CMakePackage`, `CudaPackage`, and/or `ROCmPackage`, you must import them using the following code in the `packages.py` file:
```
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage
```
And for other spack-related functions, import:
```
from spack.package import *
```
