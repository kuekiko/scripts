#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <string.h>
#define MAX_INPUT_SIZE 10240

typedef void* (*ParseRecvDataFunc)(void*, const char*);
typedef void* (*CIsDiscoveryFunc)(void *);

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s input_file\n", argv[0]);
        return 1;
    }

    void *handle;
    char *error;
    CIsDiscoveryFunc CIsDiscovery;
    ParseRecvDataFunc parseRecvData;


    handle = dlopen("/data/local/tmp/libxxx.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "%s\n", dlerror());
        exit(EXIT_FAILURE);
    }

    // 打开输入文件
    FILE* input_file = fopen(argv[1], "r");
    if (input_file == NULL) {
        perror("Failed to open input file");
        return 1;
    }


    // 分配输入缓冲区
    uint8_t input_buffer[MAX_INPUT_SIZE];

    // 读取输入文件内容到输入缓冲区
    size_t bytes_read = fread(input_buffer, 1, MAX_INPUT_SIZE, input_file);

    // 关闭输入文件
    fclose(input_file);

    // 检查是否成功读取输入文件
    if (bytes_read == 0) {
        fprintf(stderr, "Failed to read input file\n");
        return 1;
    }

    // 命令行输入
    // uint8_t input_buffer[MAX_INPUT_SIZE];
    // size_t bytes_read = fread(input_buffer, 1, sizeof(input_buffer), stdin);
    // if (bytes_read == 0) {
    //     fprintf(stderr, "Failed to read input data from stdin\n");
    //     dlclose(handle);
    //     return 1;
    // }


    CIsDiscovery = (CIsDiscoveryFunc)dlsym(handle, "_ZN4SADP12CIsDiscoveryC2Ev");
    if (CIsDiscovery == NULL) {
        printf("Failed to get function pointer: %s\n", dlerror());
        dlclose(handle);
        return 1;
    }
    error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "%s\n", error);
        exit(EXIT_FAILURE);
    }

    parseRecvData = (ParseRecvDataFunc)dlsym(handle, "_ZN4SADP12CIsDiscovery13ParseRecvDataEPKcj");
    if (!parseRecvData) {
        printf("Failed to get function pointer for ParseRecvData: %s\n", dlerror());
        dlclose(handle);
        return 1;
    }
    
    error = dlerror();
    if (error != NULL) {
        fprintf(stderr, "%s\n", error);
        exit(EXIT_FAILURE);
    }
    
    printf("----TEST-----\n");
    printf("CIsDiscovery_pt: %p\n", CIsDiscovery);
    printf("parseRecvData_pt: %p\n", parseRecvData);
    // 分配一段内存用来存储CIsDiscovery对象
    void* cdis = malloc(0x1000);
    memset(cdis,0,0x1000);
    void* result = CIsDiscovery(cdis);
    printf("Result: %p\n", result);
    printf("cdis: %p\n", cdis);
    // char *xml = "<xml>aaaa</xml>";
    void* pres = parseRecvData(cdis,(const char *)input_buffer);
    printf("pres: %p\n", pres);
    // 返回值可能为 0xffffffff 0x0 
    if(pres == 0xffffffff){
        printf("input ERR\n");
    }
    if(pres == 0x0){
        printf("Type = hello\n");
    }
    free(cdis);
    // free(result);
    dlclose(handle);
    return 0;
}