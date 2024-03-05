from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy
from typing import List


class Component():
    def __init__(self, name, requires, libs, required_components=None, boost_extensions=None):
        self.name = name
        self.requires = requires
        self.libs = libs
        self.required_components = [] if required_components is None else required_components
        self.boost_extensions = [] if boost_extensions is None else boost_extensions

    def get_exports_sources(self):
        return ((f"{self.name}/src", "*"),
                (f"{self.name}/include", "*"),
                (f"{self.name}/cmake", "*"),
                (f"{self.name}/tests", "*"),
                (f"{self.name}/", "CMakeLists.txt"))

    def get_option(self):
        return f"with_{self.name}"

    def get_cmake_variable_name(self):
        return self.get_option()


fmt = "fmt/9.1.0"
# boost = "boost/1.76.0"

a = Component(
    name="a",
    requires=(fmt,),
    libs=["a"],
    boost_extensions=["container"],
)

b = Component(
    name="b",
    requires=(fmt,),
    libs=["b"],
)

c = Component(
    name="c",
    requires=(fmt,),
    libs=["c"],
    required_components=[a],
)

class Commons(ConanFile):
    version = "0.1"
    _all_boost_extensions: List[str] = ["atomic", "chrono", "container", "context", "contract", "coroutine",
                                        "date_time", "exception", "fiber", "filesystem", "graph", "graph_parallel",
                                        "iostreams", "json", "locale", "log", "math", "mpi", "nowide",
                                        "program_options", "python", "random", "regex", "serialization", "stacktrace",
                                        "system", "test", "thread", "timer", "type_erasure", "wave"]
    _all_components: List[Component] = [a,b,c]
    _enabled_components: List[Component] = []
    name = "minimal_example"
    license = "<Put the package license here>"
    author = "<author>"
    url = "<url>"
    description = "Library contains other libraries (choose some of them using conan options)"
    topics = ("a", "b", "c")
    settings = "os", "compiler", "build_type", "arch"
    options = {**{component.get_option(): [True, False, ''] for component in _all_components},
               "shared": [True, False],
               "fPIC": [True, False]}
    default_options = {**{component.get_option(): False for component in _all_components},
                       **{f"boost/*:without_{extension_name}": True for extension_name in _all_boost_extensions},
                       "shared": False, "fPIC": True, "di/*:with_extensions": True}
    generators = "CMakeDeps", "CMakeToolchain"

    def export_sources(self):
        self._copy("CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder, keep_path=True)
        self._copy("*", src=f"{self.recipe_folder}/cmake/", dst=f"{self.export_sources_folder}/cmake", keep_path=True)
        for component in self._all_components:
            for [path, pattern] in component.get_exports_sources():
                self._copy(pattern, src=f"{self.recipe_folder}/{path}", dst=f"{self.export_sources_folder}/{path}",
                           keep_path=True)

    def get_boost_options(self):
        enabled_boost_extensions = [extension for component in self._enabled_components for extension in
                                    component.boost_extensions]
        if (len(enabled_boost_extensions) == 0):  # prevent boost compilation error by enabling at least one extension
            enabled_boost_extensions = ["container"]
        return {f"without_{extension}": False for extension in enabled_boost_extensions}

    def configure(self):
        self._enable_components()
        self._enable_components_required_components()
        boost_options = self.get_boost_options()
        for extension_name in boost_options:
            setattr(self.options["boost"], extension_name, boost_options[extension_name])

    def _enable_components(self):
        for component in self._all_components:
            if self._is_enabled_in_options(component):
                self._enable_component(component)
        if len(self._enabled_components) == 0:
            print("WARNING: all components are disabled. Preparing all components")
            [self._enable_component(component) for component in self._all_components]

    def _enable_components_required_components(self):
        for component in self._enabled_components:
            for required_component in component.required_components:
                self._enable_component(required_component)

    def _is_enabled_in_options(self, component: Component) -> bool:
        try:
            return getattr(self.options, component.get_option())
        except:
            return False

    def _enable_component(self, component):
        if component not in self._enabled_components:
            self._enabled_components.append(component)

    def requirements(self):
        already_defined = []
        for component in self._enabled_components:
            print(f"COMPONENTS: {component}")
            for requirement in component.requires:
                print(f"REQUIREMENTS: {component.requires}")
                print(f"REQUIREMENT: {requirement}")
                to_be_enabled = requirement not in already_defined
                if requirement not in already_defined:
                    already_defined.append(requirement)
                if to_be_enabled and requirement != fmt:
                    self.requires(requirement, transitive_headers=True, transitive_libs=True)
        if fmt in already_defined:
            self.requires(fmt, force=True, transitive_headers=True,
                          transitive_libs=True)  # solve potencial dependencies conflicts

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _set_cmake_variable(self, cmake_toolchain, component):
        cmake_toolchain.variables[component.get_cmake_variable_name()] = "True"

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake_toolchain = CMakeToolchain(self)
        cmake = CMake(self)
        cmake.verbose = True
        [self._set_cmake_variable(cmake_toolchain, component) for component in self._enabled_components]
        cmake.configure()
        cmake.build()

    def _package_component(self, component_name):
        self._copy("*", src=f"{self.source_folder}/{component_name}/include",
                   dst=f"{self.package_folder}/include/")
        if self.settings.build_type == "Debug":
            self._copy("*", src=f"{self.source_folder}/{component_name}/src",
                       dst=f"{self.package_folder}/src/{component_name}", keep_path=False)

    def package(self):
        [self._package_component(component.name) for component in self._enabled_components]
        self._copy("*.lib", src=self.build_folder, dst=f"{self.package_folder}/lib", keep_path=False)
        self._copy("*.dll", src=self.build_folder, dst=f"{self.package_folder}/bin", keep_path=False)
        self._copy("*.dylib*", src=self.build_folder, dst=f"{self.package_folder}/lib", keep_path=False)
        self._copy("*.so", src=self.build_folder, dst=f"{self.package_folder}/lib", keep_path=False)
        self._copy("*.a", src=self.build_folder, dst=f"{self.package_folder}/lib", keep_path=False)

    def _set_up_libs(self, component):
        self.cpp_info.components[component.name].libs = component.libs

    def _set_component_requires_another(self):
        for component in self._enabled_components:
            for required_component in component.required_components:
                self.cpp_info.components[component.name].requires.append(required_component.name)

    def package_info(self):
        [self._set_up_libs(component) for component in self._enabled_components]
        self._set_component_requires_another()

    def _copy(self, pattern, src, dst, keep_path=True):
        try:
            copy(self, pattern, src=src, dst=dst, keep_path=keep_path)
        except Exception as e:
            print(f"Exception of {type(e)} occured")
