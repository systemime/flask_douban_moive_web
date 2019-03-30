import requests
from flask import current_app
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature, SignatureExpired
from app.settings import Operations
from app.models import User
from app.helpers.redis_utils import add_email_task_to_redis, email_task


def save_image(image_url, cate):
    # 传入图片url 保存到本地
    assert cate in ['avatar', 'celebrity', 'movie']
    if cate == 'avatar':
        base_path = os.path.join(current_app.config['UPLOAD_PATH'], 'avatar')

    if cate == 'celebrity':
        base_path = os.path.join(
            current_app.config['UPLOAD_PATH'], 'celebrity')

    if cate == 'movie':
        base_path = os.path.join(current_app.config['UPLOAD_PATH'], 'movie')

    file_name = image_url.split('/')[-1]

    with open(os.path.join(base_path, file_name), 'wb') as file:
        file.write(requests.get(image_url).content)


def query_by_id_list(document, id_list):
    """@param document : object ``app.models.*`` 
    @param id_list :document.id ``list`` 
    """
    return [document.objects(id=id, is_deleted=False).first() for id in id_list if id_list]


def generate_email_confirm_token(username, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'username': username, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data).decode('ascii')


def validate_email_confirm_token(token, operation, user=None, new_password=None,new_email=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation'):
        return False
    username = data.get('username')
    if operation == Operations.CONFIRM:
        email = data.get('email')
        user = User.objects(username=username, email=email, is_deleted=False).first()
        if not user:
            return False
        user.update(confirmed_email=True)

    elif operation == Operations.RESET_PASSWORD:
        user = User.objects(username=username, is_deleted=False).first()
        if not user:
            return False
        user.set_password(new_password)
        
    elif operation == Operations.CHANGE_EMAIL:
        if new_email is None:
            return False
        user = User.objects(username=username, is_deleted=False).first()
        if not user:
            return False
        if User.objects(email=new_email,is_deleted=False).first() is not None:
            return False
        try:
            user.update(email=new_email,confirmed_email=False)
            user.reload()
            send_confirm_email_task = email_task(
                user, cate=Operations.CONFIRM)
            add_email_task_to_redis(send_confirm_email_task)
        except:
            return False
    else:
        return False
    return True
