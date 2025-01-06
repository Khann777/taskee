from rest_framework import serializers

from account.models import CustomUser
from .models import TeamMember, Team

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id',)

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'
        read_only_fields = ('id',)

class AddTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'

    def validate(self, data):
        team = data.get('team')
        user = self.context['request'].user

        # Проверяем, что пользователь является лидером команды
        if team and user != team.leader:
            raise serializers.ValidationError({"detail": "You are not the leader of this team."})
        if team.members.filter(user=user).exists():
            raise serializers.ValidationError({"detail": "You are already a member of this team."})

        team.members.add(user)
        team.save()
        return data

class RemoveTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'
        read_only_fields = ('id',)

    def validate(self, data):
        team = data.get('team')
        user = self.context['request'].user

        if team and user != team.leader:
            raise serializers.ValidationError({"detail": "You are not the leader of this team."})
        if not team.members.filter(user=user).exists():
            raise serializers.ValidationError({"detail": "You are not a member of this team."})

        team.members.remove(user)
        team.save()
        return data

