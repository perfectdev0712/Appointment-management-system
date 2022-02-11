eEffect instead.');\n    } finally {\n      if (previousFiber) {\n        setCurrentFiber(fiber);\n      } else {\n        resetCurrentFiber();\n      }\n    }\n  }\n}\n\nvar didWarnStateUpdateForUnmountedComponent = null;\n\nfunction warnAboutUpdateOnUnmountedFiberInDEV(fiber) {\n  {\n    var tag = fiber.tag;\n\n    if (tag !== HostRoot && tag !== ClassComponent && tag !== FunctionComponent && tag !== ForwardRef && tag !== MemoComponent && tag !== SimpleMemoComponent && tag !== Block) {\n      // Only warn for user-defined components, not internal ones like Suspense.\n      return;\n    } // If there are pending passive effects unmounts for this Fiber,\n    // we can assume that they would have prevented this update.\n\n\n    if ((fiber.flags & PassiveUnmountPendingDev) !== NoFlags) {\n      return;\n    } // We show the whole stack but dedupe on the top component's name because\n    // the problematic code almost always lies inside that component.\n\n\n    var componentName = getComponentName(fiber.type) || 'ReactComponent';\n\n    if (didWarnStateUpdateForUnmountedComponent !== null) {\n      if (didWarnStateUpdateForUnmountedComponent.has(componentName)) {\n        return;\n      }\n\n      didWarnStateUpdateForUnmountedComponent.add(componentName);\n    } else {\n      didWarnStateUpdateForUnmountedComponent = new Set([componentName]);\n    }\n\n    if (isFlushingPassiveEffects) ; else {\n      var previousFiber = current;\n\n      try {\n        setCurrentFiber(fiber);\n\n        error(\"Can't perform a React state update on an unmounted component. This \" + 'is a no-op, but it indicates a memory leak in your application. To ' + 'fix, ca