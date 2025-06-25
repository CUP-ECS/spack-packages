## About:
CUP-ECS internal spack package respository.

## Setup:

  1. Clone spack from https://github.com/spack/spack.
  2. Set up your environment so that the ~/.spack directory is created.
  3. Register this repository by adding the following lines to your ~/.spack/repos.yaml file:
  4. Use spack normally. Spack will automatically find libraries included in this repository.
```
repos:
  cupecs:
    git: git@github.com:CUP-ECS/spack-packages.git
    destination: ~/cupecs # Modify to where you want this repository cloned
```

## Package Creation:
Create a directory with the name of your package in `spack_pkgs/spack_repo/cupecs/packages` and place your `package.py` file in that directory.

For packages that include `CMakePackage`, `CudaPackage`, and/or `ROCmPackage`, you must import them using the following code in the `packages.py` file:
```
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage
```
And for other spack-related functions, import:
```
from spack.package import *
```
