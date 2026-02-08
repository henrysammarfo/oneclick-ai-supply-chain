import { run } from "hardhat";
import fs from "fs";
import path from "path";

/**
 * Verify all deployed contracts on Blockscout
 */

async function main() {
  console.log("🔍 Starting contract verification on Creditcoin Testnet Blockscout...\n");

  // Load deployment addresses
  const deploymentPath = path.join(__dirname, "..", "deployments", "creditcoin-testnet.json");

  if (!fs.existsSync(deploymentPath)) {
    throw new Error("Deployment file not found. Please deploy contracts first.");
  }

  const deployment = JSON.parse(fs.readFileSync(deploymentPath, "utf-8"));
  const contracts = deployment.contracts;

  console.log("📦 Verifying Test Tokens...\n");

  // Verify Test Tokens
  const testTokens = ["TestUSDC", "TestUSDT", "TestDAI", "TestETH", "TestWBTC"];
  for (const token of testTokens) {
    const tokenName = token.replace("Test", "t");
    const address = contracts.testTokens[tokenName];

    console.log(`Verifying ${tokenName} at ${address}...`);
    try {
      await run("verify:verify", {
        address: address,
        constructorArguments: [],
      });
      console.log(`✅ ${tokenName} verified\n`);
    } catch (error: any) {
      if (error.message.includes("Already Verified")) {
        console.log(`✅ ${tokenName} already verified\n`);
      } else {
        console.log(`❌ ${tokenName} verification failed:`, error.message, "\n");
      }
    }
  }

  // Verify CredToken
  console.log(`Verifying CredToken at ${contracts.credToken}...`);
  try {
    await run("verify:verify", {
      address: contracts.credToken,
      constructorArguments: [],
    });
    console.log("✅ CredToken verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ CredToken already verified\n");
    } else {
      console.log("❌ CredToken verification failed:", error.message, "\n");
    }
  }

  // Verify USCAttestor
  console.log(`Verifying USCAttestor at ${contracts.uscAttestor}...`);
  try {
    await run("verify:verify", {
      address: contracts.uscAttestor,
      constructorArguments: [],
    });
    console.log("✅ USCAttestor verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ USCAttestor already verified\n");
    } else {
      console.log("❌ USCAttestor verification failed:", error.message, "\n");
    }
  }

  // Verify CreditScoring
  console.log(`Verifying CreditScoring at ${contracts.creditScoring}...`);
  try {
    await run("verify:verify", {
      address: contracts.creditScoring,
      constructorArguments: [],
    });
    console.log("✅ CreditScoring verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ CreditScoring already verified\n");
    } else {
      console.log("❌ CreditScoring verification failed:", error.message, "\n");
    }
  }

  // Verify CreditNFT
  console.log(`Verifying CreditNFT at ${contracts.creditNFT}...`);
  try {
    await run("verify:verify", {
      address: contracts.creditNFT,
      constructorArguments: [],
    });
    console.log("✅ CreditNFT verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ CreditNFT already verified\n");
    } else {
      console.log("❌ CreditNFT verification failed:", error.message, "\n");
    }
  }

  // Verify InterestRateStrategy
  console.log(`Verifying InterestRateStrategy at ${contracts.interestRateStrategy}...`);
  try {
    await run("verify:verify", {
      address: contracts.interestRateStrategy,
      constructorArguments: [contracts.creditScoring],
    });
    console.log("✅ InterestRateStrategy verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ InterestRateStrategy already verified\n");
    } else {
      console.log("❌ InterestRateStrategy verification failed:", error.message, "\n");
    }
  }

  // Verify ATokens, VariableDebtTokens, StableDebtTokens
  console.log("📦 Verifying Token Implementations...\n");

  const assets = ["tUSDC", "tUSDT", "tDAI", "tETH", "tWBTC"];
  for (const asset of assets) {
    const underlyingAddress = contracts.testTokens[asset];

    // AToken
    console.log(`Verifying a${asset} at ${contracts.aTokens[asset]}...`);
    try {
      await run("verify:verify", {
        address: contracts.aTokens[asset],
        constructorArguments: [underlyingAddress, `CredLend ${asset}`, `a${asset}`],
      });
      console.log(`✅ a${asset} verified\n`);
    } catch (error: any) {
      if (error.message.includes("Already Verified")) {
        console.log(`✅ a${asset} already verified\n`);
      } else {
        console.log(`❌ a${asset} verification failed:`, error.message, "\n");
      }
    }

    // VariableDebtToken
    console.log(`Verifying variableDebt${asset} at ${contracts.variableDebtTokens[asset]}...`);
    try {
      await run("verify:verify", {
        address: contracts.variableDebtTokens[asset],
        constructorArguments: [
          underlyingAddress,
          `CredLend Variable Debt ${asset}`,
          `variableDebt${asset}`,
        ],
      });
      console.log(`✅ variableDebt${asset} verified\n`);
    } catch (error: any) {
      if (error.message.includes("Already Verified")) {
        console.log(`✅ variableDebt${asset} already verified\n`);
      } else {
        console.log(`❌ variableDebt${asset} verification failed:`, error.message, "\n");
      }
    }

    // StableDebtToken
    console.log(`Verifying stableDebt${asset} at ${contracts.stableDebtTokens[asset]}...`);
    try {
      await run("verify:verify", {
        address: contracts.stableDebtTokens[asset],
        constructorArguments: [
          underlyingAddress,
          `CredLend Stable Debt ${asset}`,
          `stableDebt${asset}`,
        ],
      });
      console.log(`✅ stableDebt${asset} verified\n`);
    } catch (error: any) {
      if (error.message.includes("Already Verified")) {
        console.log(`✅ stableDebt${asset} already verified\n`);
      } else {
        console.log(`❌ stableDebt${asset} verification failed:`, error.message, "\n");
      }
    }
  }

  // Verify LendingPool
  console.log(`Verifying LendingPool at ${contracts.lendingPool}...`);
  try {
    await run("verify:verify", {
      address: contracts.lendingPool,
      constructorArguments: [contracts.creditScoring, contracts.credToken],
    });
    console.log("✅ LendingPool verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ LendingPool already verified\n");
    } else {
      console.log("❌ LendingPool verification failed:", error.message, "\n");
    }
  }

  // Verify FlashLoan
  console.log(`Verifying FlashLoan at ${contracts.flashLoan}...`);
  try {
    await run("verify:verify", {
      address: contracts.flashLoan,
      constructorArguments: [contracts.creditScoring],
    });
    console.log("✅ FlashLoan verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ FlashLoan already verified\n");
    } else {
      console.log("❌ FlashLoan verification failed:", error.message, "\n");
    }
  }

  // Verify CredLendGovernor
  console.log(`Verifying CredLendGovernor at ${contracts.governor}...`);
  try {
    await run("verify:verify", {
      address: contracts.governor,
      constructorArguments: [contracts.credToken],
    });
    console.log("✅ CredLendGovernor verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ CredLendGovernor already verified\n");
    } else {
      console.log("❌ CredLendGovernor verification failed:", error.message, "\n");
    }
  }

  // Verify SafetyModule
  console.log(`Verifying SafetyModule at ${contracts.safetyModule}...`);
  try {
    await run("verify:verify", {
      address: contracts.safetyModule,
      constructorArguments: [contracts.credToken],
    });
    console.log("✅ SafetyModule verified\n");
  } catch (error: any) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ SafetyModule already verified\n");
    } else {
      console.log("❌ SafetyModule verification failed:", error.message, "\n");
    }
  }

  console.log("\n🎉 ========================");
  console.log("🎉 VERIFICATION COMPLETE!");
  console.log("🎉 ========================\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Verification failed:");
    console.error(error);
    process.exit(1);
  });
