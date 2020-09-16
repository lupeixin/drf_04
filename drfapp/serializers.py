from rest_framework import serializers, exceptions
from rest_framework.serializers import ModelSerializer

from drf_04 import settings
from drfapp.models import Book, Press


class PressModelSerializer(ModelSerializer):
    """
    出版社序列化器
    """

    class Meta:
        model = Press
        fields = ("press_name", "address", "pic")


class BookModelSerializer(ModelSerializer):
    """
    图书的序列化器
    """
    # 自定义字段（不推荐）
    # content = serializers.SerializerMethodField()
    #
    # def get_content(self, obj):
    #     return "content"

    pic = serializers.SerializerMethodField()

    def get_pic(self, obj):
        print(obj.pic)
        url = f'http://127.0.0.1:8000{settings.MEDIA_URL}{obj.pic}'
        return url

    # TODO 自定义序列化器连表查询  查询图书时将对应的出版社的信息查询出来
    #     # 可以在图书的序列化器中去嵌套一个序列化器来完成多表查询
    #     # 必须与模型中的外键名保持一致  在连表查询较多字段时使用
    publish = PressModelSerializer()

    class Meta:
        model = Book
        # 指定你要序列化模型的具体字段
        fields = ("book_name", "price", "pic", "publish")
        # 查询表的所有字段
        # fields = "__all__"
        # 指定不展示哪些字段
        # exclude = ("is_delete", "status", "id")
        # 指定查询的深度
        # depth = 1


class BookModelDeSerializer(ModelSerializer):
    """
    图书的反序列化
    """

    class Meta:
        model = Book
        fields = ("book_name", "price", "publish", "authors")
        extra_kwargs = {
            "book_name": {
                "max_length": 15,
                "min_length": 2,
                "error_messages": {
                    "max_length": "长度太长了",
                    "min_length": "长度太短了",
                }
            },
            "price": {
                "required": True,
                "decimal_places": 2,
            }
        }

    # 全局钩子同样适用于 ModelSerializer
    def validate(self, attrs):
        name = attrs.get("book_name")
        book = Book.objects.filter(book_name=name)
        if book:
            raise exceptions.ValidationError('图书已存在')
        return attrs

    # 局部钩子的使用  验证每个字段
    def validate_price(self, obj):
        # 价格不能超过100
        if obj > 100:
            raise exceptions.ValidationError("价格最多不能超过100")
        return obj


class BookModelSerializerV2(ModelSerializer):
    """
    序列化器与反序列化器整合
    """

    class Meta:
        model = Book
        # 指定的字段  填序列化与反序列所需字段并集
        fields = ("book_name", "price", "pic", "publish", "authors")

        # 添加DRF的校验规则  可以通过此参数指定哪些字段只参加序列化  哪些字段只参加反序列化
        extra_kwargs = {
            "book_name": {
                "max_length": 15,
                "min_length": 2,
            },
            # 只参与反序列化
            "publish": {
                "write_only": True,  # 指定此字段只参与反序列化
            },
            "authors": {
                "write_only": True,
            },
            # 只参与序列化
            "pic": {
                "read_only": True,  # 指定此字段只参与序列化
            }
        }

    # 全局钩子同样适用于 ModelSerializer
    def validate(self, attrs):
        name = attrs.get("book_name")
        book = Book.objects.filter(book_name=name)
        if book:
            raise exceptions.ValidationError('图书已存在')
        return attrs

    # 局部钩子的使用  验证每个字段
    def validate_price(self, obj):
        # 价格不能超过100
        if obj > 100:
            raise exceptions.ValidationError("价格最多不能超过100")
        return obj

    # 重写update方法完成更新
    # def update(self, instance, validated_data):
    #     book_name = validated_data.get("book_name")
    #     instance.book_name = book_name
    #     instance.save()
    #     return instance

