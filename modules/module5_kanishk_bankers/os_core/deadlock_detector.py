# modules/module5_kanishk_bankers/os_core/deadlock_detector.py
# Author: Kanishk Ramola
# OS Concept: Deadlock Detection & Resource Allocation Graph (RAG)

class DeadlockDetector:
    def __init__(self, num_processes, num_resources, availableResources, allocatedResources, requestMatrix, process_names=None):
        self.num_processes = num_processes
        self.num_resources = num_resources
        self.availableResources = list(availableResources)
        self.allocatedResources = [list(row) for row in allocatedResources]
        self.requestMatrix = [list(row) for row in requestMatrix]
        self.process_names = process_names or [f"Patient_P{i}" for i in range(self.num_processes)]

        self.waitingQueue = []
        self.blockedProcesses = []
        self.resourceGraph = {}
        self.deadlockStatus = "No Deadlock"

    def build_resource_graph(self):
        self.resourceGraph = {p: [] for p in self.process_names}
        for i in range(self.num_processes):
            for r in range(self.num_resources):
                if self.requestMatrix[i][r] > 0:
                    for j in range(self.num_processes):
                        if i != j and self.allocatedResources[j][r] > 0:
                            p_from = self.process_names[i]
                            p_to = self.process_names[j]
                            if p_to not in self.resourceGraph[p_from]:
                                self.resourceGraph[p_from].append(p_to)
        return self.resourceGraph

    def detect_deadlock(self):
        work = list(self.availableResources)
        finish = [True] * self.num_processes

        for i in range(self.num_processes):
            has_allocation = any(self.allocatedResources[i][j] > 0 for j in range(self.num_resources))
            if has_allocation:
                finish[i] = False

        while True:
            found = False
            for i in range(self.num_processes):
                if not finish[i]:
                    can_satisfy = True
                    for j in range(self.num_resources):
                        if self.requestMatrix[i][j] > work[j]:
                            can_satisfy = False
                            break

                    if can_satisfy:
                        for j in range(self.num_resources):
                            work[j] += self.allocatedResources[i][j]
                        finish[i] = True
                        found = True

            if not found:
                break

        self.blockedProcesses = []
        for i in range(self.num_processes):
            if not finish[i]:
                self.blockedProcesses.append(self.process_names[i])

        if self.blockedProcesses:
            self.deadlockStatus = f"Deadlock Detected: {len(self.blockedProcesses)} processes stuck!"
            has_deadlock = True
        else:
            self.deadlockStatus = "No Deadlock (System running smoothly)"
            has_deadlock = False

        self.build_resource_graph()
        return has_deadlock, self.blockedProcesses, self.deadlockStatus
