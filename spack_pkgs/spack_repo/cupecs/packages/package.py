# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import sys

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage

from spack.package import *


class HypreCmake(CMakePackage, CudaPackage):
    """Hypre is a library of high performance preconditioners that
    features parallel multigrid methods for both structured and
    unstructured grid problems."""

    homepage = "https://computing.llnl.gov/project/linear_solvers/software.php"
    url = "https://github.com/hypre-space/hypre/archive/v2.14.0.tar.gz"
    git = "https://github.com/hypre-space/hypre.git"

    maintainers("ulrikeyang", "osborn9", "balay")

    test_requires_compiler = True

    license("Apache-2.0")

    version("develop", branch="master")
    version("2.33.0", sha256="0f9103c34bce7a5dcbdb79a502720fc8aab4db9fd0146e0791cde7ec878f27da")
    version("2.32.0", sha256="2277b6f01de4a7d0b01cfe12615255d9640eaa02268565a7ce1a769beab25fa1")
    version("2.31.0", sha256="9a7916e2ac6615399de5010eb39c604417bb3ea3109ac90e199c5c63b0cb4334")
    version("2.30.0", sha256="8e2af97d9a25bf44801c6427779f823ebc6f306438066bba7fcbc2a5f9b78421")
    version("2.29.0", sha256="98b72115407a0e24dbaac70eccae0da3465f8f999318b2c9241631133f42d511")
    version("2.28.0", sha256="2eea68740cdbc0b49a5e428f06ad7af861d1e169ce6a12d2cf0aa2fc28c4a2ae")
    version("2.27.0", sha256="507a3d036bb1ac21a55685ae417d769dd02009bde7e09785d0ae7446b4ae1f98")
    version("2.26.0", sha256="c214084bddc61a06f3758d82947f7f831e76d7e3edeac2c78bb82d597686e05d")
    version("2.25.0", sha256="f9fc8371d91239fca694284dab17175bfda3821d7b7a871fd2e8f9d5930f303c")
    version("2.24.0", sha256="f480e61fc25bf533fc201fdf79ec440be79bb8117650627d1f25151e8be2fdb5")
    version("2.23.0", sha256="8a9f9fb6f65531b77e4c319bf35bfc9d34bf529c36afe08837f56b635ac052e2")
    version("2.22.1", sha256="c1e7761b907c2ee0098091b69797e9be977bff8b7fd0479dc20cad42f45c4084")
    version("2.22.0", sha256="2c786eb5d3e722d8d7b40254f138bef4565b2d4724041e56a8fa073bda5cfbb5")

    variant(
        "shared",
        default=(sys.platform != "darwin"),
        description="Build shared library (disables static library)",
    )
    variant(
        "superlu_dist", default=False, description="Activates support for SuperLU_Dist library"
    )
    variant("int64", default=False, description="Use 64bit integers")
    variant("mixedint", default=False, description="Use 64bit integers while reducing memory use")
    variant("complex", default=False, description="Use complex values")
    variant("mpi", default=True, description="Enable MPI support")
    variant("openmp", default=False, description="Enable OpenMP support")
    variant("debug", default=False, description="Build debug instead of optimized version")
    variant("unified_memory", default=False, description="Use unified memory")

    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated
    depends_on("fortran", type="build")  # generated

    depends_on("mpi", when="+mpi")
    depends_on("blas")
    depends_on("lapack")
    depends_on("superlu-dist", when="+superlu_dist+mpi")

    conflicts("+cuda", when="+int64")
    conflicts("+unified_memory", when="~cuda")

    def url_for_version(self, version):
        if version >= Version("2.12.0"):
            url = f"https://github.com/hypre-space/hypre/archive/v{version}.tar.gz"
        else:
            url = f"https://computing.llnl.gov/project/linear_solvers/download/hypre-{version}.tar.gz"

        return url

    root_cmakelists_dir = "src"

    def cmake_args(self):
        from_variant = self.define_from_variant
        args = [
            from_variant("HYPRE_WITH_MPI", "mpi"),
            from_variant("HYPRE_WITH_OPENMP", "openmp"),
            from_variant("HYPRE_WITH_BIGINT", "int64"),
            from_variant("HYPRE_WITH_MIXEDINT", "mixedint"),
            from_variant("HYPRE_WITH_COMPLEX", "complex"),
            from_variant("BUILD_SHARED_LIBS", "shared"),
            from_variant("HYPRE_ENABLE_SHARED", "shared"),
            from_variant("HYPRE_WITH_DSUPERLU", "superlu_dist"),
            from_variant("HYPRE_WITH_CUDA", "cuda"),
            from_variant("HYPRE_ENABLE_UNIFIED_MEMORY", "unified_memory"),
        ]

        return args

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        if self.spec.satisfies("+cuda"):
            env.set("CUDA_HOME", self.spec["cuda"].prefix)
            env.set("CUDA_PATH", self.spec["cuda"].prefix)
            cuda_arch = self.spec.variants["cuda_arch"].value
            if cuda_arch:
                arch_sorted = list(sorted(cuda_arch, reverse=True))
                env.set("HYPRE_CUDA_SM", arch_sorted[0])
            # In CUDA builds hypre currently doesn't handle flags correctly
            env.append_flags("CXXFLAGS", "-O2" if self.spec.satisfies("~debug") else "-g")

    extra_install_tests = join_path("src", "examples")

    @run_after("install")
    def cache_test_sources(self):
        if "+mpi" not in self.spec:
            print("Package must be installed with +mpi to cache test sources")
            return

        cache_extra_test_sources(self, self.extra_install_tests)

        # Customize the examples makefile before caching it
        makefile = join_path(install_test_root(self), self.extra_install_tests, "Makefile")
        filter_file(r"^HYPRE_DIR\s* =.*", f"HYPRE_DIR = {self.prefix}", makefile)
        filter_file(r"^CC\s*=.*", "CC = " + self.spec["mpi"].mpicc, makefile)
        filter_file(r"^F77\s*=.*", "F77 = " + self.spec["mpi"].mpif77, makefile)
        filter_file(r"^CXX\s*=.*", "CXX = " + self.spec["mpi"].mpicxx, makefile)
        filter_file(
            r"^LIBS\s*=.*",
            r"LIBS = -L$(HYPRE_DIR)/lib64 -lHYPRE -lm $(CUDA_LIBS) $(DOMP_LIBS)",
            makefile,
        )

    @property
    def _cached_tests_work_dir(self):
        """The working directory for cached test sources."""
        return join_path(self.test_suite.current_test_cache_dir, self.extra_install_tests)

    def test_bigint(self):
        """Perform smoke tests on installed HYPRE package."""
        if "+mpi" not in self.spec:
            raise SkipTest("Package must be installed with +mpi to run tests")

        # Build and run cached examples
        with working_dir(self._cached_tests_work_dir):
            make = which("make")
            make("bigint")

            for exe_name in ["ex5big", "ex15big"]:
                with test_part(self, f"test_bigint_{exe_name}", purpose=f"Ensure {exe_name} runs"):
                    program = which(exe_name)
                    if program is None:
                        raise SkipTest(f"{exe_name} does not exist in version {self.version}")

                    program()

    @property
    def headers(self):
        """Export the main hypre header, HYPRE.h; all other headers can be found
        in the same directory.
        Sample usage: spec['hypre'].headers.cpp_flags
        """
        hdrs = find_headers("HYPRE", self.prefix.include, recursive=False)
        return hdrs or None

    @property
    def libs(self):
        """Export the hypre library.
        Sample usage: spec['hypre'].libs.ld_flags
        """
        is_shared = self.spec.satisfies("+shared")
        libs = find_libraries("libHYPRE", root=self.prefix, shared=is_shared, recursive=True)
        return libs or None
