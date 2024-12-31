#include <stdio.h>
#include <pthread.h>

/*线程一*/
void thread_1(int i)
{
    printf("This is a pthread_%d\n", i);
    sleep(1);
}

int main(void)
{
    pthread_t id_1;
    int i, ret;
    /*创建线程一*/
    for (int i = 0; i < 5; i++) {
        ret = pthread_create(&id_1, NULL, (void *)thread_1, (void *)i);
        if (ret != 0)
        {
            printf("Create pthread error!\n");
            return 1;
        }
        /*等待线程结束*/
        // pthread_join(id_1, NULL);
    }

    return 0;
}
