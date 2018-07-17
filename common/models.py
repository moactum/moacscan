from django.db import models
from django.utils import timezone

# Create your models here.
class TimeStampedModel(models.Model):
	created = models.DateTimeField(auto_now_add=True,editable=False)
	changed = models.DateTimeField(default=timezone.now,editable=False)
	updated = models.DateTimeField(auto_now =True,editable=False)

	class Meta:
		abstract = True

class TokenTopic(models.Model):
	hash = models.CharField(max_length=66,unique=True)
	class Meta:
		pass
	def __str__(self):
		return self.hash

class TokenType(models.Model):
	name = models.CharField(max_length=16,unique=True)
	class Meta:
		pass
	def __str__(self):
		return self.name

EVENT_SIGNATURES = {
	"0x7805862f689e2f13df9f062ff482ad3ad112aca9e0847911ed832e158c525b33" : "",
	"0x48335238b4855f35377ed80f164e8c6f3c366e54ac00b96a6402d4a9814a03a5" : "",
	"0xa59785389b00cbd19745afbe8d59b28e3161395c6b1e3525861a2b0dede0b90d" : "",
	"0xcc16f5dbb4873280815c1ee09dbd06736cffcc184412cf7a71a0fdb75d397ca5" : "",
	"0xa9c8dfcda5664a5a124c713e386da27de87432d5b668e79458501eb296389ba7" : "",
	"0x8c32c568416fcf97be35ce5b27844cfddcd63a67a1a602c3595ba5dac38f303a" : "",
	"0xfff3c900d938d21d0990d786e819f29b8d05c1ef587b462b939609625b684b16" : "",
	"0x92ca3a80853e6663fa31fa10b99225f18d4902939b4c53a9caae9043f6efd004" : "",
	"0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c" : "",
	"0x0a5311bd2a6608f08a180df2ee7c5946819a649b204b554bb8e39825b2c50ad5" : "",
	"0x98dcaeced95369821fc42e6b1e87d724bad86c549e4d6f1b69cc88eeb1154387" : "",
	"0xf230e9bff1db5b4b83eeb7d668d810c0d390981603a6ffcd12cc8cbc049a490b" : "",
	"0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" : "Transfer(address,address,uint256)",
	"0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925" : "Approval(address,address,uint256)",
	"0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31" : "ApprovalForAll(address,address,bool)",
}
