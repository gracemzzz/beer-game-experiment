# Exact development prompts and returned choices

Eight isolated assistant responses, two per condition/candidate. No parent conversation was passed. These are development outputs, not GPT-6 / Pro website measurements or human observations.

## a01: plain_deadline, brief, repetition 1

Exact prompt: [PLAIN_DEADLINE_BRIEF.md](PLAIN_DEADLINE_BRIEF.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":10,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":8},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":16},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":24},{"id":"t10","order":8},{"id":"t11","order":8},{"id":"t12","order":0},{"id":"t13","order":40},{"id":"t14","order":16},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":8},{"id":"t19","order":8},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":24},{"id":"t26","order":8},{"id":"t27","order":4},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":16},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

## a02: plain_deadline, ample, repetition 1

Exact prompt: [PLAIN_DEADLINE_AMPLE.md](PLAIN_DEADLINE_AMPLE.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":180,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":12},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":20},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":28},{"id":"t10","order":8},{"id":"t11","order":12},{"id":"t12","order":0},{"id":"t13","order":40},{"id":"t14","order":24},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":4},{"id":"t19","order":8},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":32},{"id":"t26","order":8},{"id":"t27","order":0},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":24},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

## a03: plain_deadline, brief, repetition 2

Exact prompt: [PLAIN_DEADLINE_BRIEF.md](PLAIN_DEADLINE_BRIEF.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":10,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":8},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":16},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":24},{"id":"t10","order":8},{"id":"t11","order":8},{"id":"t12","order":0},{"id":"t13","order":40},{"id":"t14","order":16},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":8},{"id":"t19","order":8},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":24},{"id":"t26","order":8},{"id":"t27","order":4},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":16},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

## a04: plain_deadline, ample, repetition 2

Exact prompt: [PLAIN_DEADLINE_AMPLE.md](PLAIN_DEADLINE_AMPLE.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":180,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":8},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":16},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":28},{"id":"t10","order":4},{"id":"t11","order":8},{"id":"t12","order":0},{"id":"t13","order":44},{"id":"t14","order":20},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":8},{"id":"t19","order":8},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":24},{"id":"t26","order":8},{"id":"t27","order":0},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":16},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

## b01: countdown, brief, repetition 1

Exact prompt: [COUNTDOWN_BRIEF.md](COUNTDOWN_BRIEF.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":10,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":12},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":16},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":24},{"id":"t10","order":8},{"id":"t11","order":12},{"id":"t12","order":0},{"id":"t13","order":40},{"id":"t14","order":16},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":8},{"id":"t19","order":12},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":24},{"id":"t26","order":8},{"id":"t27","order":0},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":16},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

## b02: countdown, ample, repetition 1

Exact prompt: [COUNTDOWN_AMPLE.md](COUNTDOWN_AMPLE.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":180,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":8},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":16},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":24},{"id":"t10","order":8},{"id":"t11","order":8},{"id":"t12","order":0},{"id":"t13","order":40},{"id":"t14","order":16},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":8},{"id":"t19","order":8},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":24},{"id":"t26","order":8},{"id":"t27","order":0},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":16},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

## b03: countdown, brief, repetition 2

Exact prompt: [COUNTDOWN_BRIEF.md](COUNTDOWN_BRIEF.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":10,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":8},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":16},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":24},{"id":"t10","order":8},{"id":"t11","order":8},{"id":"t12","order":0},{"id":"t13","order":40},{"id":"t14","order":16},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":8},{"id":"t19","order":8},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":24},{"id":"t26","order":8},{"id":"t27","order":0},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":16},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

## b04: countdown, ample, repetition 2

Exact prompt: [COUNTDOWN_AMPLE.md](COUNTDOWN_AMPLE.md). Raw response:

```json
{"schema_version":"pressure-framing-development-v1","deadline_seconds":180,"choices":[{"id":"t01","order":16},{"id":"t02","order":0},{"id":"t03","order":8},{"id":"t04","order":0},{"id":"t05","order":40},{"id":"t06","order":16},{"id":"t07","order":8},{"id":"t08","order":0},{"id":"t09","order":24},{"id":"t10","order":4},{"id":"t11","order":8},{"id":"t12","order":0},{"id":"t13","order":40},{"id":"t14","order":16},{"id":"t15","order":0},{"id":"t16","order":0},{"id":"t17","order":24},{"id":"t18","order":0},{"id":"t19","order":8},{"id":"t20","order":0},{"id":"t21","order":32},{"id":"t22","order":8},{"id":"t23","order":8},{"id":"t24","order":0},{"id":"t25","order":24},{"id":"t26","order":8},{"id":"t27","order":0},{"id":"t28","order":0},{"id":"t29","order":40},{"id":"t30","order":16},{"id":"t31","order":8},{"id":"t32","order":0}],"complete":true}
```

