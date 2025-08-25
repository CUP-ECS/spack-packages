# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

from spack.package import *

class Tessera(CMakePackage, CudaPackage, ROCmPackage):
    """Distributed and GPU-accelerated unstructured mesh library"""

    homepage = "https://github.com/JStewart28/Tessera.git"
    git = "https://github.com/JStewart28/Tessera.git"
    url = "https://github.com/JStewart28/Tessera/archive/refs/tags/v0.1.0.tar.gz"

    maintainers("JStewart28")

    license("BSD-3-Clause")

    version("develop", branch="develop", submodules=True)
    version("master", branch="main", submodules=True)
    version("0.1.0", tag="v0.1.0", submodules=True)
    
    # Backend variants to build on GPU systems and pass the right
    # informtion to the packages we depend on
    variant("cuda", default=False, description="Use CUDA support from subpackages")
    variant("openmp", default=False, description="Use OpenMP support from subpackages")
    
    # Library-specific variants
    variant("testing", default=False, description="Build unit tests")
    variant("examples", default=False, description="Build tutorial examples")
    #
    
    depends_on("c", type="build")
    depends_on("cxx", type="build")

    # Kokkos
    depends_on("kokkos @4:")
    depends_on("kokkos +cuda +cuda_lambda +cuda_constexpr", when="+cuda")
    depends_on("kokkos +rocm", when="+rocm")
    depends_on("kokkos +wrapper", when="+cuda%gcc")

    # Cabana: propagate CUDA and AMD GPU targets to Cabana
    depends_on("cabana@master +mpi+grid")
    for cuda_arch in CudaPackage.cuda_arch_values:
        depends_on("cabana +cuda cuda_arch=%s" % cuda_arch, when="+cuda cuda_arch=%s" % cuda_arch)
    for amdgpu_value in ROCmPackage.amdgpu_targets:
        depends_on(
            "cabana +rocm amdgpu_target=%s" % amdgpu_value,
            when="+rocm amdgpu_target=%s" % amdgpu_value
        )
    
    # Google test
    # depends_on("googletest", type="build")

    # Variants are primarily backends to build on GPU systems and pass the right
    # informtion to the packages we depend on
    # variant("cuda", default=False, description="Use CUDA support from subpackages")
    # variant("openmp", default=False, description="Use OpenMP support from subpackages")

    # MPI dependencies
    depends_on("mpi")
    with when("+cuda"):
        depends_on("mpich +cuda", when="^[virtuals=mpi] mpich")
        depends_on("mvapich +cuda", when="^[virtuals=mpi] mvapich")
        depends_on("mvapich2 +cuda", when="^[virtuals=mpi] mvapich2")
        depends_on("mvapich2-gdr +cuda", when="^[virtuals=mpi] mvapich2-gdr")
        depends_on("openmpi +cuda", when="^[virtuals=mpi] openmpi")

    with when("+rocm"):
        depends_on("mpich +rocm", when="^[virtuals=mpi] mpich")
        depends_on("mvapich2-gdr +rocm", when="^[virtuals=mpi] mvapich2-gdr")
    
    # Propagate cuda architectures down to Kokkos and optional submodules
    for arch in CudaPackage.cuda_arch_values:
        cuda_dep = "+cuda cuda_arch={0}".format(arch)
        depends_on("kokkos {0}".format(cuda_dep), when=cuda_dep)

    for arch in ROCmPackage.amdgpu_targets:
        rocm_dep = "+rocm amdgpu_target={0}".format(arch)
        depends_on("kokkos {0}".format(rocm_dep), when=rocm_dep)

    conflicts("+cuda", when="cuda_arch=none")
    conflicts("+rocm", when="amdgpu_target=none")
    
    # VTK dependencies
    depends_on("vtk @9.4.1 +mpi")

    # If we're using CUDA or ROCM, require MPIs be GPU-aware
    conflicts("mpich ~cuda", when="+cuda")
    conflicts("mpich ~rocm", when="+rocm")
    conflicts("openmpi ~cuda", when="+cuda")
    conflicts("^intel-mpi")  # Heffte won't build with intel MPI because of needed C++ MPI support
    # Commenting so we can test C++20 and cuda@12.2.1 on Lassen
    # conflicts("^spectrum-mpi", when="^cuda@11.3:") # cuda-aware spectrum is broken with cuda 11.3:


    def patch(self):
        # CMakeLists.txt tries to enable C when MPI is requsted, but too late:
        filter_file("LANGUAGES CXX", "LANGUAGES C CXX", "CMakeLists.txt")

    # CMake specific build functions
    # CMake specific build functions
    def cmake_args(self):

        # options = [self.define_from_variant("BUILD_SHARED_LIBS", "shared")]
        options = []
        
        enable = ["TESTING", "EXAMPLES"]
        # require = ["MPI", "CABANA"]

        for category, cname in zip([enable], ["ENABLE"]):
            for var in category:
                cbn_option = "Tessera_{0}_{1}".format(cname, var)
                options.append(self.define_from_variant(cbn_option, var.lower()))

        # Attempt to disable find_package() calls for disabled options(if option supports it):
        # for var in require:
            # if not self.spec.satisfies("+" + var.lower()):
                # options.append(self.define("CMAKE_DISABLE_FIND_PACKAGE_" + var, "ON"))

        # Use hipcc for HIP.
        if self.spec.satisfies("+rocm"):
            options.append(self.define("CMAKE_CXX_COMPILER", self.spec["hip"].hipcc))

        # Use hipcc as the c compiler if we are compiling for rocm. Doing it this way
        # keeps the wrapper insted of changeing CMAKE_CXX_COMPILER keeps the spack wrapper
        # and the rpaths it sets for us from the underlying spec.
        if self.spec.satisfies("+rocm"):
            env["SPACK_CXX"] = self.spec["hip"].hipcc

        # If we're building with cray mpich, we need to make sure we get the GTL library for
        # gpu-aware MPI
        if self.spec.satisfies("+rocm ^cray-mpich"):
            gtl_dir = join_path(self.spec["cray-mpich"].prefix, "..", "..", "..", "gtl", "lib")
            args.append(
                "-DCMAKE_EXE_LINKER_FLAGS=-Wl,-rpath={0} -L{0} -lmpi_gtl_hsa".format(gtl_dir)
            )
        elif self.spec.satisfies("+cuda ^cray-mpich"):
            gtl_dir = join_path(self.spec["cray-mpich"].prefix, "..", "..", "..", "gtl", "lib")
            args.append(
                "-DCMAKE_EXE_LINKER_FLAGS=-Wl,-rpath={0} -L{0} -lmpi_gtl_cuda".format(gtl_dir)
            )

        # Use hipcc as the c compiler if we are compiling for rocm. Doing it this way
        # keeps the wrapper insted of changeing CMAKE_CXX_COMPILER keeps the spack wrapper
        # and the rpaths it sets for us from the underlying spec.
        if self.spec.satisfies("+rocm"):
            env["SPACK_CXX"] = self.spec["hip"].hipcc

        # If we're building with cray mpich, we need to make sure we get the GTL library for
        # gpu-aware MPI
        if self.spec.satisfies("+rocm ^cray-mpich"):
            gtl_dir = join_path(self.spec["cray-mpich"].prefix, "..", "..", "..", "gtl", "lib")
            args.append(
                "-DCMAKE_EXE_LINKER_FLAGS=-Wl,-rpath={0} -L{0} -lmpi_gtl_hsa".format(gtl_dir)
            )
        elif self.spec.satisfies("+cuda ^cray-mpich"):
            gtl_dir = join_path(self.spec["cray-mpich"].prefix, "..", "..", "..", "gtl", "lib")
            args.append(
                "-DCMAKE_EXE_LINKER_FLAGS=-Wl,-rpath={0} -L{0} -lmpi_gtl_cuda".format(gtl_dir)
            )

        return options
