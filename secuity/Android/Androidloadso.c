#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

int main(int argc, char **argv) {
    void *handle;
    char *error;
    int (*func1)(void *,int, int), (*func2)();

    handle = dlopen("/data/local/tmp/xxx.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "%s\n", dlerror());
        exit(EXIT_FAILURE);
    }

    dlerror();

    func1 = (int (*)(int, int)) dlsym(handle, "FUNC1");
    func2 = (int (*)(int, int)) dlsym(handle, "FUNC2");

    error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "%s\n", error);
        exit(EXIT_FAILURE);
    }
    char *addr = "1111111111111\n";
    printf("----------TEST-----------");
    printf("%d\n", (*func1)(addr,1, 2));
    printf("%d\n", (*func2)(1, 2));

    dlclose(handle);
    exit(EXIT_SUCCESS);
}