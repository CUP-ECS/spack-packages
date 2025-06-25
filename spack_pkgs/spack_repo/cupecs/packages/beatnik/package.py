# In your custom repository (e.g., namespace 'mycustom')
# in a package file, e.g., mycustom_mpich/package.py

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

# Import the original Mpich class from the 'builtin' repository
from spack_repo.builtin.packages.mpich.package import Beatnik as BuiltinBeatnik

from spack.package import *

class MycustomMpich(BuiltinBeatnik):

    # Add new dependencies

    # VTK dependencies
    depends_on("vtk @9.4.1 +mpi")
    
    # NuMesh dependency
    depends_on("numesh@develop")
    
    # We need updated CMake args for GPU-aware MPI on cray-mpich
    def cmake_args(self):
        args = []

        # Point to BLT appropriately
        args.append("-DBLT_SOURCE_DIR={0}".format(self.spec["blt"].prefix))
        
        # Add numesh
        # args.append("-DNUMESH_DIR={0}".format(self.spec["numesh"].prefix))

        # Use hipcc as the c compiler if we are compiling for rocm. Doing it this way
        # keeps the wrapper insted of changeing CMAKE_CXX_COMPILER keeps the spack wrapper
        # and the rpaths it sets for us from the underlying spec.
        if self.spec.satisfies("+rocm"):
            env["SPACK_CXX"] = self.spec["hip"].hipcc

        # If we're building with cray mpich, we need to make sure we get the GTL library for
        # gpu-aware MPI, since cabana and beatnik require it
        if self.spec.satisfies("+rocm ^cray-mpich"):
            gtl_dir = join_path(self.spec["cray-mpich"].prefix, "..", "..", "..", "gtl", "lib")
            args.append(
                "-DCMAKE_EXE_LINKER_FLAGS=-Wl,-rpath={0} -L{0} -lmpi_gtl_hsa".format(gtl_dir)
            )
            # Assuming we are on Tioga, addd NuMesh
            args.append("-DNuMesh_PREFIX=~/install-tioga/numesh")
        elif self.spec.satisfies("+cuda ^cray-mpich"):
            gtl_dir = join_path(self.spec["cray-mpich"].prefix, "..", "..", "..", "gtl", "lib")
            args.append(
                "-DCMAKE_EXE_LINKER_FLAGS=-Wl,-rpath={0} -L{0} -lmpi_gtl_cuda".format(gtl_dir)
            )
        return args

    def install(self, spec, prefix):
        if "+custom_feature" in spec:
            # Do custom things
            pass
        super().install(spec, prefix) # Call parent install method