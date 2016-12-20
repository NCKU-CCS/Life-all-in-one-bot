from rest_framework import viewsets, serializers
from .models import TextCloud, FSM


# class TextCloudSerializer(serializers.ModelSerializer):

    # menu_items = MenuItemRelatedSerializer(many=True)

    # class Meta:
        # model = TextCloud

class TextCloudViewSet(viewsets.ModelViewSet):
	true_search = TextCloud.objects.filter(flag=True)
	true_list = list()
	for foo in true_search:
		tmp = {
			"count": foo.number,
			"keyword": foo.text,
		}
		true_list.append(tmp)
	false_search = TextCloud.objects.filter(flag=False)
	false_list = list()
	for foo in false_search:
		tmp = {
			"count": foo.number,
			"keyword": foo.text,
		}
		false_list.append(tmp)
	queryset = json.dumps({"most": true_list, "lack": false_list})
    # queryset = Store.objects.all()
    serializer_class = TextCloudSerializer