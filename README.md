## About:
CUP-ECS internal spack package respository.

## Setup:

  1. Clone spack from https://github.com/spack/spack.
  2. Clone this repository.
  3. Set up your environment so that the ~/.spack directory is created.
  4. Find the `repos.yaml` file in the `~/.spack` directory. If you are on a cluster, the `repos.yaml` file will be in `~./spack/{cluster name}/`, for example on tioga, `~./spack/tioga/`. Sometimes spack does not create the `repos.yaml` file for you. If so, create it yourself in the correct directory.
  5. Register this repository by adding the following lines to the `repos.yaml` file:
```
repos:
  cupecs: /path/to/repo/spack-packages/spack_pkgs/spack_repo/cupecs
```
  6. Run `spack repo list` to verify spack has found the cupecs package repository. The output should be similar to:
```
bash:$ spack repo ls
[+] cupecs     v2.0    /path/to/repo/spack-packages/spack_pkgs/spack_repo/cupecs
[+] builtin    v2.2    ~/.spack/package_repos/fncqgg4/repos/spack_repo/builtin
```
  7. Use spack normally. Spack will automatically find libraries included in this repository.


## Package Creation:
Create a directory with the name of your package in `spack_pkgs/spack_repo/cupecs/packages` and place your `package.py` file in that directory.

For packages that include `CMakePackage`, `CudaPackage`, and/or `ROCmPackage`, you must include the following imports in your `packages.py` file:
```
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage
```
And for other spack-related functions, import:
```
from spack.package import *
```
