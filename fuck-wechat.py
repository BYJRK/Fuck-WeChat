from pathlib import Path
import shutil
from progressbar.shortcuts import progressbar

# 记录一下所有垃圾的总大小
total_trash_size = 0


def remove_trash():
    """删除微信的所有缓存"""
    global total_trash_size
    # 找到微信的存储目录
    wechat_dir = Path.home() / "Documents" / "WeChat Files"
    # 记录所有垃圾文件和文件夹的路径，用来之后进行删除
    trash_list = []

    print('开始扫描微信的缓存文件...')
    print('=' * 30)
    # All Users 目录存储了所有登录过的用户使用过的头像
    trash_list.extend(find_trash(
        wechat_dir / "All Users", '*.jpg', '已登录过用户的头像图片'))

    # Applet 目录存储了所有小程序的缓存
    applet_dir = wechat_dir / "Applet"
    trash_list.extend(find_trash(applet_dir, '*', '公用小程序缓存'))

    # 获取所有登录过的用户产生的缓存文件
    for d in wechat_dir.iterdir():
        if d.name not in ['Applet', 'All Users']:
            trash_list.extend(get_user_trashes(d))

    print('=' * 30)
    print(f'总垃圾大小：{total_trash_size:.3f} MB')

    print('请注意，以上垃圾包含所有下载（点开）过的图片、视频、文本文件，请谨慎删除！')
    user_input = input('是否清除全部垃圾？y(es)/n(o) > ')
    if user_input.lower() not in ['y', 'yes']:
        return

    print('开始清理垃圾...')
    for p in progressbar(trash_list, redirect_stdout=True):
        if not remove_file_or_folder(p):
            total_trash_size -= get_size(p)
    print(f'本次共清理垃圾 {total_trash_size:.3f} MB')


def get_user_trashes(user_dir: Path):
    """获取指定微信用户目录下的所有垃圾"""
    trash_list = []
    print(f'在用户 {user_dir.name} 的目录下，共发现：')
    # 小程序缓存（简直有毒，一个全局的还不够，每个用户还得单独再缓存一遍）
    trash_list.extend(find_trash(user_dir / 'Applet', title='小程序缓存', indent=1))

    # Attachment，Backup，BackupFiles，CustomEmotions 都是空的

    # Data 不知道干什么用的，但是不大，先不删了

    # FavTemp 不知道是什么，但是应该没用，可以删
    trash_list.extend(find_trash(user_dir / 'FavTemp', title=''))

    # 表情包文件缓存
    trash_list.extend(find_trash(
        user_dir / 'CustomEmoV1', title='表情文件缓存', indent=1))

    # Image, Video, Files 都是空的
    file_storage = user_dir / 'FileStorage'
    # 其下是以形如 2020-06 的文件夹存储的各种图片缩略图缓存文件
    trash_list.extend(find_trash(
        file_storage / 'Cache', title='缩略图文件', indent=1))
    # 又又又一个表情图片缓存
    trash_list.extend(find_trash(
        file_storage / 'CustomEmotion', title='自定义表情文件缓存', indent=1))
    # 下载到本地的文件
    trash_list.extend(find_trash(
        file_storage / 'File', title='已下载文件', indent=1))
    # 未知缓存文件，在微信运行中被占用，无法删除
    trash_list.extend(find_trash(file_storage / 'Fav', title='未知文件', indent=1))
    # 图片文件
    trash_list.extend(find_trash(
        file_storage / 'Image', title='图片数据文件', indent=1))
    # 视频文件
    trash_list.extend(find_trash(
        file_storage / 'Video', title='视频文件', indent=1))
    # 表情包图标文件
    trash_list.extend(find_trash(file_storage / 'General' /
                                 'Data', title='表情图标文件', indent=1))
    # 高清头像图片
    trash_list.extend(find_trash(file_storage / 'General' /
                                 'HDHeadImage', title='高清头像图片', indent=1))
    # ResUpdate 里面只有损坏的压缩包，不知道是干什么用的，但肯定没卵用
    trash_list.extend(find_trash(
        user_dir / 'ResUpdate', title='未知垃圾文件', indent=1))

    return trash_list


def find_trash(d: Path, glob='*', title='缓存', indent=0):
    """获取某个垃圾文件夹的信息"""
    if not d.exists():
        return []
    global total_trash_size
    total_size = 0
    trash_list = []
    for p in d.glob(glob):
        total_size += get_size(p)
        trash_list.append(p)
    # 如果传入 title 为空，则不输出信息，仅记录垃圾文件的路径
    if not title:
        return trash_list
    # 开头的缩进
    if indent > 0:
        title = '\t' * indent + title
    # 输出信息
    print(f'{title}：{total_size:.3f} MB')
    total_trash_size += total_size
    return trash_list


def remove_file_or_folder(p: Path):
    """删除文件或文件夹"""
    try:
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p.absolute())
        else:
            # 见鬼去吧
            pass
        return True
    except:
        print(f'无法删除 {p.absolute()}')
        return False


def get_size(p: Path):
    """获取一个文件或文件夹的大小"""
    # 如果是文件
    if p.is_file():
        return p.stat().st_size / 1048576  # 以 MB 为单位
    # 如果是文件夹
    elif p.is_dir():
        # 获取其下所有文件的大小之和
        return sum([get_size(f) for f in p.rglob('*') if f.is_file()])
    # 我不知道除了文件和文件夹以外还有别的什么类型，但是如果有，让它见鬼去吧
    return 0


if __name__ == "__main__":
    remove_trash()
