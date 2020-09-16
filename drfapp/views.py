from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drfapp.models import Book
from drfapp.serializers import BookModelSerializer, BookModelDeSerializer, BookModelSerializerV2


class BookAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        查询接口
        :param request:
        :return:
        """
        book_id = kwargs.get("id")
        if book_id:
            book_obj = Book.objects.filter(id=book_id).first()
            if book_obj:
                data = BookModelSerializer(book_obj).data
                return Response({
                    "status": 200,
                    "message": "查询单个图书成功",
                    "results": data
                })
            else:
                return Response({
                    "status": 400,
                    "message": "查询单个图书失败/图书不存在",
                })
        else:
            book_all = Book.objects.all()
            book_list = BookModelSerializer(book_all, many=True).data
            return Response({
                "status": 200,
                "message": "查询所有图书成功",
                "results": book_list
            })

    def post(self, request, *args, **kwargs):
        data = request.data
        s = BookModelDeSerializer(data=data)
        # 校验数据, raise_exception=True 只要数据校验失败就马上抛出异常
        s.is_valid(raise_exception=True)
        book_obj = s.save()

        return Response({
            "status": 201,
            "message": "创建图书成功",
            "results": BookModelSerializer(book_obj).data
        })


class BookAPIViewV2(APIView):
    """
    整合序列化器后的视图
    """

    def get(self, request, *args, **kwargs):
        """
        查询图书信息的接口
        :param request:
        :return:
        """
        book_id = kwargs.get("id")
        if book_id:
            # 查询单个图书
            book_obj = Book.objects.get(pk=book_id, is_delete=False)
            data = BookModelSerializerV2(book_obj).data
            return Response({
                "status": 200,
                "message": "查询单个图书成功",
                "results": data
            })
        else:
            objects_all = Book.objects.filter(is_delete=False)
            book_list = BookModelSerializerV2(objects_all, many=True).data
            return Response({
                "status": 200,
                "message": "查询所有成功",
                'results': book_list
            })

    def post(self, request, *args, **kwargs):
        """
        新增单个：传递参数的格式 字典
        新增多个：[{},{},{}]  列表中嵌套字典  每一个字典是一个图书对象
        :param request:
        :return:
        """
        request_data = request.data
        if isinstance(request_data, dict):  # 代表添加单个对象
            many = False
        elif isinstance(request_data, list):  # 代表添加多个对象
            many = True
        else:
            return Response({
                "status": 400,
                "message": "数据格式有误"
            })

        book_ser = BookModelSerializerV2(data=request_data, many=many)
        book_ser.is_valid(raise_exception=True)
        save = book_ser.save()

        return Response({
            "status": 200,
            "message": '添加图书成功',
            "results": BookModelSerializerV2(save, many=many).data
        })

    def delete(self, request, *args, **kwargs):
        """
        删除单个以及删除多个
        单个删除：获取删除的id  根据id删除  通过动态路由传参 v2/books/1/  {ids:[1,]}
        删除多个：有多个id的时候 {ids:[1,2,3]}
        """
        book_id = kwargs.get("id")

        if book_id:
            # 删除单个  将删除单个转换为删除多个的参数形式
            ids = [book_id]
        else:
            # 删除多个
            ids = request.data.get("ids")

        # 判断传递过来的图书的id是否在数据库中  且还未删除
        response = Book.objects.filter(pk__in=ids, is_delete=False).update(is_delete=True)
        print(response)
        if response:
            return Response({
                "status": status.HTTP_200_OK,
                "message": "删除成功"
            })
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "删除失败或者图书不存在",
        })

    def put(self, request, *args, **kwargs):
        """
        整体修改单个：修改一个对象的全部字段
        :return 修改后的对象
        """
        # 修改的参数
        request_data = request.data
        # 要修改的图书的id
        book_id = kwargs.get("id")
        try:
            book_obj = Book.objects.get(pk=book_id)
        except:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "图书不存在",
            })

        # 前端发送的修改的值需要做安全校验
        # 更新参数的时候使用序列化器完成数据的校验
        # TODO 如果当前要修改某个对象则需要通过instance来指定你要修改的对象
        book_ser = BookModelSerializerV2(data=request_data, instance=book_obj)
        book_ser.is_valid(raise_exception=True)
        save = book_ser.save()
        return Response({
            "status": 200,
            "message": "更新成功",
            "results": BookModelSerializerV2(save).data
        })

    def patch(self, request, *args, **kwargs):
        """
        局部更新
        """
        # 修改的参数
        request_data = request.data
        # 要修改的图书的id
        book_id = kwargs.get("id")
        try:
            book_obj = Book.objects.get(pk=book_id)
        except:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "图书不存在",
            })

        # 前端发送的修改的值需要做安全校验
        # 更新参数的时候使用序列化器完成数据的校验
        # TODO 如果当前要局部修改则需指定 partial = True即可
        book_ser = BookModelSerializerV2(data=request_data, instance=book_obj, partial=True)
        book_ser.is_valid(raise_exception=True)
        save = book_ser.save()
        return Response({
            "status": 200,
            "message": "更新成功",
            "results": BookModelSerializerV2(save).data
        })

