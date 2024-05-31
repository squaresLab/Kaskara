all: flask BehaviorTree.CPP

flask:
	docker build -t kaskara/examples:flask flask

BehaviorTree.CPP:
	docker build -t kaskara/examples:BehaviorTree.CPP BehaviorTree.CPP

.PHONY: flask BehaviorTree.CPP
