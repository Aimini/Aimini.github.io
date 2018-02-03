---
layout: post
title: C++ 继承中，成员函数的隐藏（hide）机制
date: 2018-02-03 19:48:21 +0800
description: thau you! # Add post description (optional)
img: tech.jpg # Add image post (optional)
tags: [C++, inherit, dervied, hidden, overload]
---
#     思考一个问题  
  在父类`Base`中声明一个函数`f(double x)`，在`Base`的子类`Derived`中
  声明一个成员函数`f(char c)`，那么在下述`main`函数中中对函数`f`的调用分别是哪个：  
 ```c++
 class Base {  
 public:  
     void f(double x)  
     {  
         std::cout<<"call Base::f(double)"<<std::endl;  
     };    
 };    
 class Derived : public Base {  
 public:  
     void f(char c){  
         std::cout<<"call Derived::f(char)"<<std::endl;  
     }  
 };   
 int main()  
 {  
     Derived* d = new Derived();  
     Base* b = d;  
     b->f(65.3);   
     d->f(65.3);    
     delete d;  
     return 0;  
 }
 ```

# 目录    
> * ### [导读](#导读-1)  
> * ### [环境](#环境-1)    
> * ### [测试](#测试-1)  
> * ### [结论、原因以及解决办法](#结论原因以及解决办法-1)  
> * ### [参考链接](#参考链接-1)  
> * ### [最后](#最后-1)  



 ---
# 导读  


 0.  ###     某名校高材生解读 
  以我的线性思维，`Dervied`继承自`Base`，**自然包含`Base`的所有成员**，那么`d`肯定调用`Base::f(double)`，但是是通过`Derived::f(double)`访问。  
  `f`即不是虚函数，和重写（*Override*）更是搭不上边，所以`b`调用的应该是`Base::f(double)`。  
  综上，两次都是调用`Base::f(double)`。     
   **当然，这是人脑（况且还是我的）得出的，不是电脑，自然要跑一跑才知道结果:**  
  ```bash
$ ./a.exe
call Base::f(double)
call Derived::f(char)   
  ```
  事实证明，这几年C++**白学了**，我还是too naive。  


 1.  ###     “真理”在此
  isocpp对这种情况描述如下[[1]](#参考链接-1)：
  >   *   if `Base` declares a member function `f(double x)`, and `Derived`   declares a member function f(char c) (same name but different parameter types and/or constness), then the `Base f(double x)`   is “hidden” rather than “overloaded” or “overridden” (even if the `Base`   `f(double x)`   is virtual).
  >
  >   *   Note: the hiding problem also occurs if class `Base` declares a method `f(char)`.   
  
     做一点微小的工作，稍微“翻译”一下：  
      *  只要`Dervied`中声明了同名但不同签名的函数，`Base::f`就会被隐藏。  
      *  若`Base::f(double x)`不是虚函数，在Dervied中声明了同名且同签名的函数，`Base::f`还是会被隐藏。  
  

 2. ###     验证测试  
  “真理”中没有指出“如果`Base::f(double)`为`virtual`且声明了`Derived::f(double)`”的情况，若只有一个名称为f的函数，那是重写没跑了，但若`Base`中有多个`f`的重载函数，情况就不太确定了。  
  测试主要项目包括以下几个：  
    *  不同签名  
    *  与父类virtual函数同签名  
    *  与父类普通函数同签名  
    *  什么都不干  

    验证包括：  
    * 是否为隐藏/重载
    * 是否为重写  

     在`Base`类中声明两个函数`f`，一个为`virtual`，一个是普通函数；然后在子类`Derived`中分别测试以上项目:  
```c++
class Base {
public:
    void f(double x)
    {
        std::cout<<"call Base::f(double)"<<std::endl;
    };

    virtual void f(char x)
    {
        std::cout<<"call virtual Base::f(char)"<<std::endl;
    };  
};
```

---
# 环境  

|    |  |  
| - | :- |  
| OS |  Windows7 x64 |  
| 编译器 |  g++.exe (Rev2, Built by MSYS2 project) 6.2.0 |  
|    |  |  



- - -
# 测试
### 0. 不同签名  
```c++
class Derived : public Base 
{
    public:
    void f(int c)
    {
        std::cout<<"call Derived::f(int)"<<std::endl;
    }
};

int main()
{
    Derived* d = new Derived();
    Base* b = d;
    b->f(65);  
    d->f(65);
    d->f(65.65); //want Base::f(double)
    d->f('a'); //want Base::f(char)
    delete d;
    return 0;
}
```

  `b->f(65)`报 *ambiguous* 错；因为`b`作为父类的指针，自然看不到`Derived`中的函数，`Base`中的又不知道该用哪个好。

```bash
$ /mingw64/bin/g++.exe main1.cpp
main1.cpp: In function 'int main()':
main1.cpp:28:10: error: call of overloaded 'f(int)' is ambiguous
b->f(65);
        ^
main1.cpp:5:8: note: candidate: void Base::f(double)
void f(double x)
        ^
main1.cpp:10:16: note: candidate: virtual void Base::f(char)
virtual void f(char x)
                ^
```

  注释掉后运行,结果不出所料：  

    $ ./a.exe
    call Derived::f(int)
    call Derived::f(int)
    call Derived::f(int)


### 1. 与父类virtual函数同签名  
  按照官方说明，父类中的函数依然被隐藏，只不过同签名函数是重写：  
```c++
class Derived : public Base {
public:
    void f(char c)
    {
        std::cout<<"call Derived::f(int)"<<std::endl;
    }
};

int main()
{
    Derived * d = new Derived();
    Base * b = d;
    b->f('d');  
    d->f('d');
    d->f(65.65);//want Base::f(double)
    delete d;
    return 0;
}
```

  与上次的结果看似相同，但别忘了，这次第一个call用的是`Base`的指针；从结果看，`f(char)`确实被重写、`f(double)`依然被隐藏。

```bash
$ ./a.exe
call Derived::f(int)
call Derived::f(int)
call Derived::f(int)
```

### 2.  与父类普通函数同签名

```c++
class Derived : public Base {
    public:
    void f(double c)
    {
        std::cout<<"call Derived::f(double)"<<std::endl;
    }
};

int main()
{
Derived* d = new Derived();
Base* b = d;
b->f('d');  
d->f('d'); //want Base::f(char)
d->f(65.65);
delete d;
return 0;
}
```

  运行结果表明：全部隐藏：

```bash
$ ./a.exe
call virtual Base::f(char)
call Derived::f(double)
call Derived::f(double)
```
    

###  3.  什么都不干


    class Derived : public Base {};

    int main()
    {
        Derived * d = new Derived();
        Base * b = d;
        d->f('d');      //want Base::f(char)
        d->f(65.65);    //want Base::f(double)
        delete d;
        return 0;
    }

  这次居然调用成功了：

    $ ./a.exe
    call virtual Base::f(char)
    call Base::f(double)




# 结论、原因以及解决办法

 综合上面的测试，只要在子类中有同名函数就无法通过子类的对象直接调用父类的。只不过当同名函数为普通函数时为隐藏，为`virtual`函数时则是重写。  
 至于原因可以参考官方例子和解释[[1]](#参考链接-1):  
  
  *  栗子：  
        >
        >     #include<iostream>
        >     using namespace std;
        >     class B {
        >     public:
        >         int f(int i) { cout << "f(int): "; return i+1; }
        >         // ...
        >     };
        >     class D : public B {
        >     public:
        >         double f(double d) { cout << "f(double): "; return d+1.3; }
        >         // ...
        >     };
        >     int main()
        >     {
        >         D* pd = new D;
        >         cout << pd->f(2) << '\n';
        >         cout << pd->f(2.3) << '\n';
        >         delete pd;
        >     }

  *  解释
        > In other words, there is no overload resolution between D and B. Overload resolution conceptually happens in one scope at a time: The compiler looks into the scope of D, finds the single function double f(double), and calls it. Because it found a match, it never bothers looking further into the (enclosing) scope of B. In C++, there is no overloading across scopes – derived class scopes are not an exception to this general rule. (See D&E or TC++PL4 for details).

  * 重点部分解释  
        >  因为在当前的类中通过名字找到了匹配，就不会再去父类中找。

  解决办法在官方有给出，《The C++ Programming Language》中也有小部分提及。  

  * 第一种在测试2中就可以看到——使用父类的指针或引用调用：  
```c++
int main()
{
    Derived d;
    Base* b = &d;
    Base &bref = d;
    b->f(12.2);
    bref.f(12.2);
    return 0;
}
```  

    输出：    
```bash
$ ./a.exe
call Base::f(double)
call Base::f(double)
```
  * 第二种方法：在调用时使用作用域解析符：  
```c++
int main()
{
   Derived d;
   d.Base::f(12.3);
   d.Base::f('a');
   return 0;
}
``` 
    输出：  
```bash        
$ ./a.exe
call Base::f(double)
call virtual Base::f(char)
```  
  * 第三种方法：在子类中使用using指令： 
```c++
        class Derived : public Base {
            public:
                using Base::f;
                void f(int c)
                {
                    std::cout<<"call Derived::f(int)"<<std::endl;
                }
        };

        int main()
        {
            Derived d;
            d.f(12.3);
            d.f('a');
            d.f(123);
            return 0;
        }
```  
    输出： 
```bash
$ ./a.exe
call Base::f(double)
call virtual Base::f(char)
call Derived::f(int)
```  


- - -
# 参考链接
 [[1].Inheritance — What your mother never told you](https://isocpp.org/wiki/faq/strange-inheritance)  
 [[2].Redefining vs. Overriding in C++](https://stackoverflow.com/questions/26743991/redefining-vs-overriding-in-c)

 - - -
# 最后
  * 这是本人第一次写 Blog，有什么写的不好（包括排版、风格、严谨性之类的）地方还望各位指出ヾ(´∀`o)+
  * 吐槽一下中文版的《The C++ Programming Language》，翻译真是惊到我了，还是用英文版+翻译吧。