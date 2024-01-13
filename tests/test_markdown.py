md = """

要计算文件的哈希值，可以使用哈希算法（如MD5、SHA-1或SHA-256）对文件的内容进行计算。

以下是一个使用sha256算法计算文件哈希值的示例代码：

```python
import hashlib

def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

# 使用示例
file_path = 'path/to/file.txt'
hash_value = calculate_hash(file_path)
print('File hash:', hash_value)
```

在上面的示例中，`calculate_hash`函数接受一个文件路径作为参数，并打开文件以二进制读取模式读取文件内容。然后，使用哈希对象sha256初始化，并对文件内容进行分块读取并更新哈希值。最后，通过`hexdigest`方法获取哈希值的十六进制表示。

可以根据需要更改哈希算法（如使用`hashlib.md5()`来使用MD5算法）和块大小（这里使用4096字节）。

"""

md = """
要在Ubuntu中将NTFS格式转换为ext4格式，您需要进行以下步骤：

1. 首先，确保您已经安装了gparted软件。如果没有安装，请使用以下命令进行安装：

   ```
   sudo apt update
   sudo apt install gparted
   ```

2. 然后，打开GParted软件。您可以在"应用程序"菜单中搜索并启动它。

3. 在GParted界面中，选择您想要转换格式的NTFS分区。请小心选择，确保选择正确的分区。

4. 确保分区未挂载。如果分区当前正在使用，您需要首先卸载它。在命令行中，您可以使用以下命令卸载该分区：

    ```
    sudo umount /dev/sdc1
    ```

   注意：请将"/dev/sdc1"替换为您要卸载的分区的正确路径。

5. 在GParted界面中，单击菜单中的"设备"选项，然后选择"创建"。

6. 在弹出的对话框中，选择要转换为的文件系统类型。在这种情况下，选择"ext4"。然后单击"添加"按钮。

7. 在"操作"菜单中，选择"应用所有操作"。这将开始分区格式转换的过程。

8. 等待GParted完成转换操作。这可能需要一些时间，具体取决于分区的大小和系统性能。

9. 转换完成后，您将看到分区的文件系统已更改为ext4。

10. 最后，请确保挂载分区以便访问它。您可以使用以下命令挂载该分区：

    ```
    sudo mount /dev/sdc1 /media/fuqingxu/eb63a8fa-cee9-48a5-9f05-b1388c3fda9e
    ```

    注意：请将"/dev/sdc1"替换为已转换分区的正确路径，并将"/media/fuqingxu/eb63a8fa-cee9-48a5-9f05-b1388c3fda9e"替换为您要挂载的目标路径。

请注意，在执行任何分区操作之前，务必备份重要的数据。操作不当可能导致数据丢失。



"""


md = """
要将NTFS格式转换为ext4格式，需要执行以下步骤：

1. 首先，确保你的NTFS分区已经挂载。可以使用`df -lh`命令来检查。

2. 创建一个ext4文件系统。打开终端并执行以下命令：
    ```
    sudo mkfs.ext4 /dev/sdc1
    ```
    注意将`/dev/sdc1`替换为你要转换的NTFS分区的设备名称。

3. 等待文件系统创建完成。这可能需要一些时间。

4. 将新的ext4文件系统挂载到指定的挂载点。执行以下命令：
    ```
    sudo mkdir /mnt/mydrive
    sudo mount -t ext4 /dev/sdc1 /mnt/mydrive
    ```
    注意将`/mnt/mydrive`替换为你要挂载的目录。

5. 现在，可以将数据从原始NTFS分区复制到新的ext4分区。执行以下命令：
    ```
    sudo rsync -avxP /media/fuqingxu/eb63a8fa-cee9-48a5-9f05-b1388c3fda9e /mnt/mydrive
    ```
    注意将`/media/fuqingxu/eb63a8fa-cee9-48a5-9f05-b1388c3fda9e`替换为你的原始NTFS分区的挂载点。

6. 等待数据复制完成。这可能需要一些时间，具体取决于数据量。

7. 确认数据已经成功复制到新的ext4分区后，可以卸载原始NTFS分区。执行以下命令：
    ```
    sudo umount /media/fuqingxu/eb63a8fa-cee9-48a5-9f05-b1388c3fda9e
    ```

8. 现在，你可以将新的ext4分区重新挂载到原来的位置。执行以下命令：
    ```
    sudo umount /mnt/mydrive
    sudo mount -t ext4 /dev/sdc1 /media/fuqingxu/eb63a8fa-cee9-48a5-9f05-b1388c3fda9e
    ```

完成上述步骤后，NTFS分区将被转换为ext4格式，并且数据将被复制到新的分区中。请确保在执行任何操作之前备份重要数据。


"""

def validate_path():
    import os, sys

    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # validate path so you can run from base directory
from toolbox import markdown_convertion

html = markdown_convertion(md)
# print(html)
with open("test.html", "w", encoding="utf-8") as f:
    f.write(html)
