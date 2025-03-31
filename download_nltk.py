import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print("开始下载NLTK资源...")
nltk.download('punkt')
print("NLTK资源下载完成！") 