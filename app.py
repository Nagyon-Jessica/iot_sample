import io, os, json, base64, datetime, urllib
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/plot')
def plot_graph():
    image = io.BytesIO()
    date1 = []
    date2 = []
    temp1 = []
    temp2 = []
    humid1 = []
    humid2 = []
    try:
        print("Azure Blob Storage v" + __version__ + " - Python quickstart sample")
        # ストレージ接続文字列の取得
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        # ストレージに接続
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        # 'iot'コンテナを取得
        container_client = blob_service_client.get_container_client("iot")
        # コンテナからBLOBを一覧取得
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            # BLOBの中身を取得
            blob_client = blob_service_client.get_blob_client("iot", blob.name)
            download_stream = blob_client.download_blob()
            # メッセージごとに分割
            json_list = download_stream.content_as_text().split("\n")
            for j in json_list:
                # JSONオブジェクトとしてパース
                packet = json.loads(j)
                # タイムスタンプを取得
                t = datetime.datetime.fromisoformat(packet['EnqueuedTimeUtc'][:-2] + '+09:00')
                # メッセージボディを取得，Base64でデコードした後JSONとしてパース
                body = json.loads(base64.standard_b64decode(packet['Body']).decode())
                # 時刻，温度，湿度をデバイスごとのリストに追加
                if body["deviceId"] == "Device1":
                    date1.append(t)
                    temp1.append(body["temperature"])
                    humid1.append(body["humidity"])
                else:
                    date2.append(t)
                    temp2.append(body["temperature"])
                    humid2.append(body["humidity"])
    except Exception as ex:
        print("Exception:")
        print(ex)

    # グラフを2行2列で並べる
    fig, ax = plt.subplots(nrows=2,ncols=2,figsize=(20, 10))
    ax[0,0].plot(date1, temp1, label='Device1: temperature')
    ax[0,1].plot(date1, humid1, color='green', label='Device1: humidity')
    ax[1,0].plot(date2, temp2, label='Device2: temperature')
    ax[1,1].plot(date2, humid2, color='green', label='Device2: humidity')
    # x軸のフォーマットを指定
    xfmt = mdates.DateFormatter("%m-%d\n%H:%M:%S")
    for i in range(2):
        for j in range(2):
            # if i == -1:
            #     ax[i,j].set_xlim(date1[0] - datetime.timedelta(days=1), date1[-1] + datetime.timedelta(days=1))
            # else:
            #     ax[i,j].set_xlim(date2[0] - datetime.timedelta(days=1), date2[-1] + datetime.timedelta(days=1))
            # グラフごとの説明を配置
            ax[i,j].legend(loc='upper right')
            ax[i,j].xaxis.set_major_formatter(xfmt)
    canvas = FigureCanvasAgg(fig)
    # グラフを画像ファイルとして書き出し
    canvas.print_png(image)
    data = urllib.parse.quote(image.getvalue())
    return data

    # response = make_response(data)
    # response.headers['Content-Type'] = 'image/png'
    # return response

@app.route('/')
def index():
    return render_template("index.html", img_data=None)

if __name__ == "__main__":
    app.run(debug=True)
