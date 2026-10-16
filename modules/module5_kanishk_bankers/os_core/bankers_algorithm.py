# modules/module5_kanishk_bankers/os_core/bankers_algorithm.py
# Author: Kanishk Ramola
# OS Concept: Banker's Algorithm (Deadlock Avoidance)

class BankersAlgorithm:
    def __init__(self, availableResources, maximumNeed, allocatedNeed, process_names=None):
        self.availableResources = list(availableResources)
        self.maximumNeed = [list(row) for row in maximumNeed]
        self.allocatedNeed = [list(row) for row in allocatedNeed]

        self.num_processes = len(self.maximumNeed)
        self.num_resources = len(self.availableResources) if self.availableResources else 0
        self.process_names = process_names or [f"Patient_P{i}" for i in range(self.num_processes)]

        self.remainingNeed = []
        self.workResources = []
        self.finishStatus = []
        self.safeSequence = []

        self.calculate_remaining_need()

    def calculate_remaining_need(self):
        self.remainingNeed = []
        for i in range(self.num_processes):
            row = []
            for j in range(self.num_resources):
                need_val = self.maximumNeed[i][j] - self.allocatedNeed[i][j]
                row.append(max(0, need_val))
            self.remainingNeed.append(row)
        return self.remainingNeed

    def is_safe_state(self):
        self.workResources = list(self.availableResources)
        self.finishStatus = [False] * self.num_processes
        self.safeSequence = []
        step_logs = []

        count = 0
        while count < self.num_processes:
            found_process = False
            for i in range(self.num_processes):
                if not self.finishStatus[i]:
                    can_allocate = True
                    for j in range(self.num_resources):
                        if self.remainingNeed[i][j] > self.workResources[j]:
                            can_allocate = False
                            break

                    if can_allocate:
                        for j in range(self.num_resources):
                            self.workResources[j] += self.allocatedNeed[i][j]

                        self.finishStatus[i] = True
                        self.safeSequence.append(self.process_names[i])
                        step_logs.append({
                            "process": self.process_names[i],
                            "work_after": list(self.workResources),
                            "action": "Completed safely & released resources"
                        })
                        found_process = True
                        count += 1

            if not found_process:
                break

        is_safe = (count == self.num_processes)
        return is_safe, self.safeSequence, step_logs

    def request_resources(self, process_index, requestedResources):
        for j in range(self.num_resources):
            if requestedResources[j] > self.remainingNeed[process_index][j]:
                return False, f"Request exceeds maximum claim for resource {j}!", []

        for j in range(self.num_resources):
            if requestedResources[j] > self.availableResources[j]:
                return False, f"Equipment currently unavailable (Resource {j})! Must wait.", []

        # Simulate allocation
        for j in range(self.num_resources):
            self.availableResources[j] -= requestedResources[j]
            self.allocatedNeed[process_index][j] += requestedResources[j]
            self.remainingNeed[process_index][j] -= requestedResources[j]

        is_safe, safe_seq, logs = self.is_safe_state()

        if is_safe:
            return True, f"Safe allocation approved. Safe sequence: {' -> '.join(safe_seq)}", safe_seq
        else:
            # Rollback
            for j in range(self.num_resources):
                self.availableResources[j] += requestedResources[j]
                self.allocatedNeed[process_index][j] -= requestedResources[j]
                self.remainingNeed[process_index][j] += requestedResources[j]
            return False, "Allocation rejected: System would enter an UNSAFE state (risk of deadlock)!", []
