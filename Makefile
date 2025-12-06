.PHONY: build-run clean wipe

# Remember to run minikube tunnel before
build-run:
	docker build . -t backend-image
	minikube image load backend-image
	kubectl apply -f pvc.yml
	kubectl apply -f k8s-deployment.yml

clean:
	kubectl delete -f k8s-deployment.yml

wipe:
	kubectl delete -f pvc.yml