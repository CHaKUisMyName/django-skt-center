from enum import Enum
import mongoengine as me
from bson import ObjectId
import datetime
import pytz

from app_organization.models.organization import Organization
from app_user.models.user import RoleUser, User
from base_models.basemodel import BaseClass, BaseEmbedded

class Issuer(BaseEmbedded):
    userId = me.ReferenceField(User)
    code = me.StringField(null= True, required= False, default = None)
    fNameEN = me.StringField(null= True, required= False, default = None)
    lNameEN = me.StringField(null= True, required= False, default = None)
    email = me.StringField(null= True, required= False, default = None)
    # roles = me.EmbeddedDocumentListField(RoleUser, null= True, required= False, default = None)


    def serialize(self):
        return {
            "userId": str(self.userId) if self.userId else None,
            "code": self.code if self.code else None,
            "fNameEN": self.fNameEN if self.fNameEN else None,
            "lNameEN": self.lNameEN if self.lNameEN else None,
            "email": self.email if self.email else None,
            # "roles": [role.serialize() for role in self.roles] if self.roles else None,
        }


class GreenYellowType(Enum):
    GreenCard = 1
    YellowCard = 2
    def serialize(self):
        return {
            "value": self.value,
            "label": self.name
        }


class IssueToType(Enum):
    Employee = 1
    Organization = 2
    Vendor = 3
    Anonymous = 4
    def serialize(self):
        return {
            "value": self.value,
            "label": self.name
        }

class YellowCardType(Enum):
    Rules = (1, {"th":"ไม่ปฏิบัติตามกฏระเบียบ", "en":"Do not follow the rules"})
    Manuals = (2, {"th":"ไม่ปฏิบัติตามคู่มือ", "en":"Do not follow the manuals"})
    Others = (3, {"th":"อื่นๆ", "en":"Others"})

    def __new__(cls, value, labels):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.labels = labels
        return obj

    def label(self, lang="th"):
        return self.labels.get(lang, self.labels.get("en"))
    
    def serialize(self):
        return {
            "value": self.value,
            "label": f"{self.labels['th']} / {self.labels['en']}"
        }


class GreenYellowCard(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    issueDate = me.DateTimeField(null=True, required=False, default=None)
    type = me.EnumField(GreenYellowType)
    issueToType = me.EnumField(IssueToType)
    issueTo = me.StringField(null=True, required=False, default=None)
    emailIssueTo = me.ListField(me.StringField(),null=True, required=False, default=None)
    issuer = me.EmbeddedDocumentField(Issuer)
    deptId = me.StringField(null=True, required=False, default=None)
    deptNameEN = me.StringField(null=True, required=False, default=None)
    yellowCardType = me.EnumField(YellowCardType, null=True, required=False, default=None)
    detail = me.StringField(null=True, required=False, default=None)
    imagePath = me.StringField(null=True, required=False, default=None)
    isActive = me.BooleanField()
    hasSendMail = me.BooleanField(default=False)
    note = me.StringField(null=True, required=False, default=None)

    meta = {
        'collection': 'greenYellowCard'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def serialize(self):
        receiver = ""
        issuer = ""
        orgIssuer = ""
        displayTypeCol = {}
        if self.issueToType.value == IssueToType.Employee.value:
            emp: User = User.objects(id = ObjectId(self.issueTo)).first()
            if emp:
                receiver = f"({emp.code}) {emp.fNameEN} {emp.lNameEN}"
        elif self.issueToType.value == IssueToType.Organization.value:
            if self.issueTo != "Foreigner":
                org: Organization = Organization.objects(id = ObjectId(self.issueTo)).first()
                receiver = f"({org.level.nameEN}) "+org.nameEN if org else ""
            else:
                receiver = "Foreigner"
        elif self.issueToType.value == IssueToType.Vendor.value:
            receiver = self.issueTo
        elif self.issueToType.value == IssueToType.Anonymous.value:
            receiver = "Unknow"
        else:
            receiver = ""
        if self.issuer:
            empployee = self.issuer.serialize()
            issuer = f"({empployee['code']}) {empployee['fNameEN']} {empployee['lNameEN']}"
            # orgIssuer = empployee['roles']

        if self.type:
            displayTypeCol = {
                "type": self.type.serialize(),
                "yellowCardType": self.yellowCardType.serialize() if self.yellowCardType else "-",
            }

        return {
            "id": str(self.id),
            "issueDate": self.issueDate.astimezone(datetime.timezone.utc).isoformat() if self.issueDate else "",
            # "issueDate": issueDateStr,
            "type": self.type.serialize() if self.type else "",
            "issueToType": self.issueToType.serialize() if self.issueToType else "",
            # "issueTo": self.issueTo if self.issueTo else "",
            "issueTo": receiver,
            "emailIssueTo": self.emailIssueTo,
            "issuer": issuer,
            "orgIssuer": orgIssuer,
            "yellowCardType": self.yellowCardType.serialize() if self.yellowCardType else "-",
            "detail": self.detail if self.detail else "-",
            "imagePath": self.imagePath if self.imagePath else "-",
            "isActive": self.isActive,
            "note": self.note if self.note else "-",
            'createDate': self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else "",
            'displayTypeCol': displayTypeCol,
            'deptId': self.deptId if self.deptId else "-",
            'deptNameEN': self.deptNameEN if self.deptNameEN else "Foreigner",
            'hasSendMail': self.hasSendMail,
        }